from odoo import models, fields, api,_
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning
import uuid
import re

class StandardSelection(models.Model):
    _name = 'standard.selection'
    _description = 'الاختيارات'

    name = fields.Char(string='الاختيار')
    replace_id = fields.Many2one('standard.replace', string='الاستبدال')

class StandarReplace(models.Model):
    _name = 'standard.replace'
    _description = 'انواع الاستبدال'
    
    name = fields.Char(string='الاستبدال')
    replace = fields.Char(string='الاختصار')
    standards = fields.Selection([
            ('many2one', 'علاقة'),
            ('char', 'نص'),
            ('integer', 'قيمة منطقية'),
            ('float', 'قيمة عشرية'),
            ('selection', 'اختيار'),
            ('date', 'تاريخ'),
            ('datetime', 'تاريخ ووقت'),
            ('sign', 'توقيع'),
            ], string='نوع الحقل المستبدل له')    
    selections = fields.One2many('standard.selection', 'replace_id', string='الاختيارات')
    standard_field = fields.Char(compute='_default_standard_field')
    
    def _default_standard_field(self):
        for replace in self:
            standard_field = False
            if replace.id:
                if replace.standards == 'sign':
                    standard_field = 'x_sign_' + str(replace.id)
                else:
                    standard_field = 'x_' + str(replace.id)
            replace.standard_field = standard_field



    models = fields.Selection(string='الموديلات', selection=lambda self: self.dynamic_selection())
    
    def dynamic_selection(self):
        models = self.env['ir.model'].sudo().search([])
        selection_list = []
        for model in models:
            field_list =[]

            field_list.append(model.model)
            field_list.append(model.name)
            selection_list.append(tuple(field_list))

        return selection_list  

    
    @api.model_create_multi
    def create(self, vals_list):
        record = super(StandarReplace, self).create(vals_list)
        replaces = self.env['standard.replace'].sudo().search([('replace', '=', record.replace),('id', '!=', record.id)])
        if len(replaces):
            raise ValidationError(_('الاختصار مستخدم من قبل'))
        else:
            fields_obj=self.env['ir.model.fields']
            standard_model = self.env['ir.model'].sudo().search([('model','=', 'standard.standard')])[0].id
            if record.standards == 'many2one':

                id=fields_obj.sudo().create({'relation':record.models,'name':'x_'+str(record.id),'field_description':record.name,'ttype':record.standards,'model_id':standard_model})

            elif record.standards == 'selection':
                select_list=[]
                for single in record.selections:
                    dic={}
                    dic['name']=single.name
                    dic['value']=single.name
                    select_list.append(dic)


                id=fields_obj.sudo().create({'selection_ids': [(0, 0, {'name':data['name'],'value':data['value']}) for data in select_list],'relation':record.models,'name':'x_'+str(record.id),'field_description':record.name,'ttype':record.standards,'model_id':standard_model})
                
            elif record.standards == 'sign':
                
                id = fields_obj.create({'relation':'res.partner','name':'x_'+str(record.id),'field_description':record.name,'ttype':'many2one','model_id':standard_model})
                signed_by = fields_obj.create({'name':'x_signed_by_'+str(record.id),'field_description':record.name,'ttype':'char','model_id':standard_model})
                signed_on = fields_obj.create({'name':'x_signed_on_'+str(record.id),'field_description':record.name,'ttype':'datetime','model_id':standard_model})
                sign = fields_obj.create({'name':'x_sign_'+str(record.id),'field_description':record.name,'ttype':'binary','model_id':standard_model})
                sign_name = fields_obj.create({'name':'x_sign_name_'+str(record.id),'field_description':record.name,'ttype':'binary','model_id':standard_model})
                
            else:
                id=fields_obj.sudo().create({'name':'x_'+str(record.id),'field_description':record.name,'ttype':record.standards,'model_id':standard_model})


            standard_view = self.env['ir.ui.view'].sudo().search([('name','=', 'النماذج الموحدة')])[0].id
            if record.standards == 'sign':
                sign_view=   """
                    <xpath expr="//group[@name='sign']" position="inside">
                        <field name="nfield" attrs="{'invisible': ['!',('original_text', 'ilike', 'replaced')]}"/>
                        <field name="sign1field" string="signature" widget="image" attrs="{'invisible': ['!',('original_text', 'ilike', 'replaced')]}"/>
                        <field name="signname"  string="signatureBy"  widget="image" attrs="{'invisible': ['!',('original_text', 'ilike', 'replaced')]}"/>                   
                    </xpath>
                    """.replace('nfield','x_'+str(record.id)).replace('sign1field','x_sign_'+str(record.id)).replace('signname','x_sign_name_'+str(record.id)).replace('replaced',str(record.replace))

                view = self.env['ir.ui.view'].create({
                    'name': 'inherit statndard_'+str(record.id),
                    'model': 'standard.standard',
                    'inherit_id':standard_view,
                    'type':'form',
                    'arch':sign_view
                    })
                groups = self.env['res.groups'].sudo().search([('id','=', 9)])              
                security = self.env['ir.rule'].create({
                    'id': 'statndard_sign_'+str(record.id),
                    'name': 'statndard_sign_'+str(record.id),
                    'model_id': standard_model,
                    'domain_force':"[('sign_id','=',user.partner_id.id)]".replace('sign_id','x_'+str(record.id)),
                    'groups':groups,
                    })
                

            else:
                view = self.env['ir.ui.view'].sudo().create({
                    'name': 'inherit statndard_'+str(record.id),
                    'model': 'standard.standard',
                    'inherit_id':standard_view,
                    'type':'form',
                    'arch': """
                        <xpath expr="//group[@name='replace']" position="inside">
                            <group>
                                <field name="nfield" attrs="{'invisible': ['!',('original_text', 'ilike', 'replaced')]}"/>
                            </group>
                        </xpath>
                    """.replace('nfield','x_'+str(record.id)).replace('replaced',str(record.replace)),
                })

        return record


    def unlink(self):
        for replace in self:
            standard_view = self.env['ir.ui.view'].sudo().search([('name','=','inherit statndard_'+str(replace.id))])
            standard_view.unlink()
            fields_obj = self.env['ir.model.fields']
            standard_model = self.env['ir.model'].sudo().search([('model','=', 'standard.standard')])[0].id
            if replace.standards == 'sign':
                security = self.env['ir.rule'].sudo().search([('name','=','statndard_sign_'+str(replace.id))])
                security.unlink()
                field_sign_id = fields_obj.sudo().search([('name','=', 'x_'+str(replace.id)),('model_id','=',standard_model)])
                field_signed_by = fields_obj.sudo().search([('name','=', 'x_signed_by_'+str(replace.id)),('model_id','=',standard_model)])
                field_signed_on = fields_obj.sudo().search([('name','=', 'x_signed_on_'+str(replace.id)),('model_id','=',standard_model)])
                field_sign = fields_obj.sudo().search([('name','=', 'x_sign_'+str(replace.id)),('model_id','=',standard_model)])
                field_sign_name = fields_obj.sudo().search([('name','=', 'x_sign_name_'+str(replace.id)),('model_id','=',standard_model)])
                if len(field_sign_id):
                    field_sign_id.unlink()
                    field_signed_by.unlink()
                    field_signed_on.unlink()
                    field_sign.unlink()
                    field_sign_name.unlink()
            else:
                field_id = fields_obj.sudo().search([('name','=', 'x_'+str(replace.id)),('model_id','=',standard_model)])

                if len(field_id):
                    field_id.unlink()
        return super(StandarReplace, self).unlink()

    
class StandardTypes(models.Model):
    _name = 'standard.types'
    _description = 'النموذج'
    
    name = fields.Char(string='النموذج')
    Text = fields.Html(string='المستند', store=True)

    replaces = fields.Text(string='الاختصارات', compute='_all_replaces')

    def _all_replaces(self):
        for types in self:
            replaces = ''
            replacements = self.env['standard.replace'].sudo().search([])
            for replacement in replacements:
                replaces += replacement.replace + ' = ' + replacement.name + '\n'
            types.replaces = replaces


class Standard(models.Model):
    _name = 'standard.standard'
    _description = 'النموذج الموحد'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    def get_portal_url_pdf_download(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        self.ensure_one()
        base_url = self.company_id.website
        access_url = base_url + '/standard_print/' + str(self.id)
        url = access_url + '%s?access_token=%s%s%s%s%s' % (
            suffix if suffix else '',
            self.access_token,
            '&report_type=%s' % report_type if report_type else '',
            '&download=true' if download else '',
            query_string if query_string else '',
            '#%s' % anchor if anchor else ''
        )
        return url
    
    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s' % (self.name)

    def _default_access_token(self):
        return str(uuid.uuid4())

    access_token = fields.Char('Security Token', required=True, default=_default_access_token, readonly=True)
    
    def action_review(self):
        for standard in self:
            standard.write({'state': 'في حالة المراجعة'})
            return True

    def action_submit(self):
        for standard in self:
            standard.write({'state': 'معتمد'})
            return True

    def action_draft(self):
        for standard in self:
            standard.write({'state': 'جديد'})
            return True

    
    name = fields.Char(string='النموذج', required=True)
    user_id = fields.Many2one('res.users', string='المسؤول', default=lambda self: self.env.user, required=True)
    partner_id = fields.Many2one('res.partner', string='مقدم الطلب', required=True)
    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company, required=True)
    state = fields.Selection([
        ('جديد', 'جديد'),
        ('في حالة المراجعة', 'في حالة المراجعة'),
        ('معتمد', 'معتمد'),
        ], string='الحالة', default='جديد')
    standard_id = fields.Many2one('standard.types', string='نوع النموذج', required=True)
    original_text = fields.Html(related='standard_id.Text')
    Text = fields.Html(string='المستند', compute='_default_standard')

    def _default_standard(self):
        for standard in self:
            note = ' '
            replaced_note = ' '
            if standard.standard_id:
                note = str(standard.original_text)
                
            replaced_note = note
            replacements = self.env['standard.replace'].sudo().search([])
            for replacement in replacements:
                name = False
                field = self._fields.get(replacement.standard_field)
                fields = field.name
                fieldm = 'object.' + fields
                if replacement.standards == 'many2one':
                    fieldm = 'object.' + fields +'.name'
                    name = eval(fieldm, {'object': standard})
                elif replacement.standards == 'sign':
                    sign_name = 'x_sign_name_' + str(replacement.id)
                    name = ('<img src="web/image?model=standard.standard&id=' + str(standard.id) +'&field=' + str(fields) + """" width='200' height='100'/>""")
                else:
                    name = eval(fieldm, {'object': standard})
                if name:
                    if replaced_note == False:
                        replaced_note = note.replace(str(replacement.replace), str(name))
                    else:
                        replaced_note = replaced_note.replace(str(replacement.replace), str(name))
            standard.Text = replaced_note

            
    sign_doc = fields.Boolean(string="Sign Document",compute="_calculate_sign_doc")

    def _calculate_sign_doc(self):
        for standard in self:
            standard_replace = self.env['standard.replace']

            data=standard
            clean = re.compile('<.*?>')   
            standard_text=data.standard_id.Text
            all_text=re.sub(clean, '', standard_text).split(' ')
            for text_each in all_text: 
                replace_ids=standard_replace.search([('replace','ilike',re.sub(clean, '', text_each)),('standards','=','sign')])
                if len(replace_ids):
                        #keep name for now
                        standard.sign_doc=True
                        break
                else:
                        standard.sign_doc=False

