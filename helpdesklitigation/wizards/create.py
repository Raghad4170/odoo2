# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Ticket(models.Model):
    _inherit = 'helpdesk.ticket'

    def create_litigation_action(self):
        for ticket in self:
            local_context = dict(
                self.env.context,
                default_ticket_id= ticket.id,
            )
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'create.litigations',
                'target': 'new',
                'context': local_context,
            }
        
    def create_consulting_action(self):
        for ticket in self:
            local_context = dict(
                self.env.context,
                default_ticket_id= ticket.id,
            )
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'create.consultings',
                'target': 'new',
                'context': local_context,
            }
        
    def create_contractconsulting_action(self):
        for ticket in self:
            local_context = dict(
                self.env.context,
                default_ticket_id= ticket.id,
            )
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'create.contractconsultings',
                'target': 'new',
                'context': local_context,
            }
        
    def attachment_action(self):
        for ticket in self:
            local_context = dict(
                self.env.context,
                default_ticket_id= ticket.id,
            )
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'moving.attachment',
                'target': 'new',
                'context': local_context,
            }
    
class attachment(models.TransientModel):
    _name = 'moving.attachment'
    _description = 'moving attachment'

    def moving_attachment(self):
        for attachment in self:
            if attachment.litigation_id:
                
                ticket_id = self.ticket_id
                rfq= self.litigation_id
                attachment = self.env['ir.attachment'].search([('res_model','=','helpdesk.ticket'), ('res_id','=', ticket_id.id)])
                attachment.write({'res_model': 'litigation.litigation', 'res_id': rfq.id,})
                messages = self.env['mail.message'].search([('model','=','helpdesk.ticket'), ('res_id','=', ticket_id.id), ('subtype_id.internal','=', False)])
                for message in messages:
                    message_values = {
                        'model': 'litigation.litigation',
                        'res_id': rfq.id,
                        'subject': message.subject,
                        'date': message.date,
                        'body': message.body,
                        'description': message.description,
                        'attachment_ids': message.attachment_ids,
                        'message_type': message.message_type,
                        'subtype_id': message.subtype_id.id,
                        'is_internal': message.is_internal,
                        'author_id': message.author_id.id,
                    }
                    new_messages = self.env['mail.message'].create(message_values)


            elif attachment.consulting_id:
                ticket_id = self.ticket_id
                rfq= self.consulting_id
                attachment = self.env['ir.attachment'].search([('res_model','=','helpdesk.ticket'), ('res_id','=', ticket_id.id)])
                attachment.write({'res_model': 'consulting.consulting', 'res_id': rfq.id,})
                messages = self.env['mail.message'].search([('model','=','helpdesk.ticket'), ('res_id','=', ticket_id.id), ('subtype_id.internal','=', False)])
                for message in messages:
                    message_values = {
                        'model': 'consulting.consulting',
                        'res_id': rfq.id,
                        'subject': message.subject,
                        'date': message.date,
                        'body': message.body,
                        'description': message.description,
                        'attachment_ids': message.attachment_ids,
                        'message_type': message.message_type,
                        'subtype_id': message.subtype_id.id,
                        'is_internal': message.is_internal,
                        'author_id': message.author_id.id,
                    }
                    new_messages = self.env['mail.message'].create(message_values)


            elif attachment.contractconsulting_id:
                ticket_id = self.ticket_id
                rfq= self.contractconsulting_id
                attachment = self.env['ir.attachment'].search([('res_model','=','helpdesk.ticket'), ('res_id','=', ticket_id.id)])
                attachment.write({'res_model': 'contractconsulting.contractconsulting', 'res_id': rfq.id,})
                messages = self.env['mail.message'].search([('model','=','helpdesk.ticket'), ('res_id','=', ticket_id.id), ('subtype_id.internal','=', False)])
                for message in messages:
                    message_values = {
                        'model': 'contractconsulting.contractconsulting',
                        'res_id': rfq.id,
                        'subject': message.subject,
                        'date': message.date,
                        'body': message.body,
                        'description': message.description,
                        'attachment_ids': message.attachment_ids,
                        'message_type': message.message_type,
                        'subtype_id': message.subtype_id.id,
                        'is_internal': message.is_internal,
                        'author_id': message.author_id.id,
                    }
                    new_messages = self.env['mail.message'].create(message_values)


    trans_type = fields.Selection([
            ('قضية', 'قضية'),
            ('استشارة', 'استشارة'),
            ('استشارة عقد', 'استشارة عقد')
            ], string='نقل إلى')
    litigation_id = fields.Many2one('litigation.litigation', string='القضية', auto_join=True)
    consulting_id = fields.Many2one('consulting.consulting', string='الاستشارة', auto_join=True)
    contractconsulting_id = fields.Many2one('contractconsulting.contractconsulting', string='استشارة العقد', auto_join=True)
    ticket_id = fields.Many2one('helpdesk.ticket', string='التذكرة')
    

class litigationticket(models.Model):
    _inherit = 'litigation.litigation'

    ticket_id = fields.Many2one('helpdesk.ticket', string='التذكرة')
    
    def action_approve(self):
        for litigation in self:
            if litigation.ticket_id:
                ticket_id = self.ticket_id
                stage_id = self.env['helpdesk.stage'].sudo().search([('clf_number','=','5')])
                ticket_id.sudo().stage_id = stage_id
        return super(litigationticket, self).action_approve()


class createlitigations(models.TransientModel):
    _name = 'create.litigations'
    _description = 'create litigations'
    
    def create_litigation(self):
        values = {
            'name': self.name,
            'summary': self.summary,
            'next_court_date': self.next_court_date,
            'establishment_date': self.establishment_date,
            'caliming_date': self.caliming_date,
            'litigation_number': self.litigation_number,
            'circuit': self.circuit,
            'user_id': self.user_id.id,
            'case_type': self.case_type,
            'court': self.court,
            'litigation_state': self.litigation_state,
            'client_state': self.client_state,
            'city': self.city,
            'company_id': self.company_id.id,
            'project_id': self.project_id.id,
            'ticket_id': self.ticket_id.id,
            'id': self.id,
        }
        record = self.env['litigation.litigation'].create(values)
        ticket_id = self.ticket_id
        rfq = record.id
        attachment = self.env['ir.attachment'].search([('res_model','=','helpdesk.ticket'), ('res_id','=', ticket_id.id)])
        attachment.write({'res_model': 'litigation.litigation', 'res_id': rfq})
        messages = self.env['mail.message'].search([('model','=','helpdesk.ticket'), ('res_id','=', ticket_id.id), ('subtype_id.internal','=', False)])
        for message in messages:
            message_values = {
                'model': 'litigation.litigation',
                'res_id': rfq,
                'subject': message.subject,
                'date': message.date,
                'body': message.body,
                'description': message.description,
                'attachment_ids': message.attachment_ids,
                'message_type': message.message_type,
                'subtype_id': message.subtype_id.id,
                'is_internal': message.is_internal,
                'author_id': message.author_id.id,
            }
            new_messages = self.env['mail.message'].create(message_values)
        stage_id = self.env['helpdesk.stage'].sudo().search([('clf_number','=','1')])
        self.ticket_id.write({'stage_id': stage_id.id})

        
    @api.depends('ticket_id')
    def get_description(self):
        if self.ticket_id.description:
            self.summary = self.ticket_id.description
            
    id = fields.Integer('ID')
    ticket_id = fields.Many2one('helpdesk.ticket', string='التذكرة')
    partner_id = fields.Many2one(related='ticket_id.partner_id', string='العميل')
    parent_id = fields.Many2one(related='partner_id.parent_id') 
    child_ids = fields.One2many(related='partner_id.child_ids') 
    name = fields.Char("القضية")
    project_id = fields.Many2one('project.project', string='المشروع')
    summary = fields.Text(string='ملخص القضية', compute='get_description', readonly=False)
    next_court_date = fields.Datetime(string='موعد الجلسة القادمة')
    establishment_date = fields.Date(string='تاريخ القيد')
    caliming_date = fields.Date(string='تاريخ الاستحقاق')
    litigation_number = fields.Char(string='رقم القضية')
    circuit = fields.Char(string='الدائرة القضائية')
    case_amount = fields.Monetary(string='مبلغ محل الدعوى', currency_field='company_currency')
    company_currency = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id')
    company_id = fields.Many2one('res.company', related='user_id.company_id', string='Company')
    user_id = fields.Many2one('res.users', related='project_id.user_id', string='المحامي')
    case_type = fields.Selection([
            ('أحوال شخصية', 'أحوال شخصية'),
            ('تنفيذ', 'تنفيذ'),
            ('جزائية', 'جزائية'),
            ('عامة', 'عامة'),
            ('عمالية', 'عمالية'),
            ('إدارية', 'إدارية'),
            ('اخرى', 'اخرى')
            ], string='نوع الدعوى')
    court = fields.Selection([
            ('المحكمة العامة', 'المحكمة العامة'),
            ('المحكمة التجارية', 'المحكمة التجارية'),
            ('المحكمة الإدارية', 'المحكمة الإدارية'),
            ('محكمة الأحوال الشخصية', 'محكمة الأحوال الشخصية'),
            ('المحكمة العمالية', 'المحكمة العمالية'),
            ('محكمة التنفيذ', 'محكمة التنفيذ'),
            ('تحكيم', 'تحكيم'),
            ('اخرى', 'اخرى')
            ], string='المحكمة')
    litigation_state = fields.Selection([
        ('تقييد الدعوى', 'تقييد الدعوى'),
        ('لم يتم قيدها', 'لم يتم قيدها'),
        ('الصلح', 'الصلح'),
        ('تسوية ودياً', 'تسوية ودياً'),
        ('قيد النظر لدى المحكمة الابتدائية', 'قيد النظر لدى المحكمة الابتدائية'),
        ('المحكمة الابتدائية', 'المحكمة الابتدائية'),
        ('حكم ابتدائي', 'حكم ابتدائي'),
        ('حكم ابتدائي لصالح العميل', 'حكم ابتدائي لصالح العميل'),
        ('حكم ابتدائي معترض عليه', 'حكم ابتدائي معترض عليه'),
        ('قيد النظر', 'قيد النظر'),
        ('قيد النظر لدى محكمة الاستئناف', 'قيد النظر لدى محكمة الاستئناف'),
        ('محكمة الاستئناف', 'محكمة الاستئناف'),
        ('عادت للمحكمة الابتدائية بملاحظات', 'عادت للمحكمة الابتدائية بملاحظات'),
        ('حكم نهائي', 'حكم نهائي'),
        ('التنفيذ', 'التنفيذ'),
        ('مشطوبة', 'مشطوبة'),
        ('التماس إعادة نظر', 'التماس إعادة نظر'),
        ('معترض عليها', 'معترض عليها'),
        ('انتهت بحكم قضائي', 'انتهت بحكم قضائي'),
        ('انتهت صلحاً', 'اانتهت صلحاً'),
        ('انتهت', 'انتهت')
        ], string='حالة القضية')
    client_state = fields.Selection([
            ('مدعي', 'مدعي'),
            ('مدعي عليه', 'مدعي عليه'),
            ('محتكم', 'محتكم'),
            ('محتكم عليه', 'محتكم عليه'),
            ('مدخل', 'مدخل'),
            ('مستأنف', 'مستأنف'),
            ('مستأنف ضده', 'مستأنف ضده')
            ], string='صفة الموكل')
    city = fields.Selection([
            ('الرياض', 'الرياض'),
            ('المدينة المنورة', 'المدينة المنورة'),
            ('جدة', 'جدة'),
            ('الخبر', 'الخبر'),
            ('مكة المكرمة','مكة المكرمة'),
            ('الاحساء','الاحساء'),
            ('الطائف','الطائف'),('ابها','ابها'),
            ('خميس مشيط','خميس مشيط'),
            ('عفيف','عفيف'),
            ('عرعر','عرعر'),
            ('أبقيق','أبقيق'),
            ('بريدة','بريدة'),
            ('بيشة','بيشة'),
            ('الباحة','الباحة'),
            ('الظهران','الظهران'),
            ('الدمام','الدمام'),
            ('ضرما','ضرما'),
            ('تبوك','تبوك'),
            ('القطيف','القطيف'),
            ('خميس مشيط','خميس مشيط'),
            ('حفر الباطن','حفر الباطن'),
            ('الجبيل','الجبيل'),
            ('الخرج','الخرج'),
            ('حائل','حائل'),
            ('نجران','نجران'),
            ('ينبع','ينبع'),
            ('صبيا','صبيا'),
            ('الدوادمي','الدوادمي'),
            ('أبو عريش','أبو عريش'),
            ('القنفذة','القنفذة'),
            ('محايل','محايل'),
            ('سكاكا','سكاكا'),
            ('عرعر','عرعر'),
            ('عنيزة','عنيزة'),
            ('القريات','القريات'),
            ('صامطة','صامطة'),
            ('جازان','جازان'),
            ('المجمعة','المجمعة'),
            ('القويعية','القويعية'),
            ('الرس','الرس'),
            ('وادي الدواسر','وادي الدواسر'),
            ('بحرة','بحرة'),
            ('الباحة','الباحة'),
            ('الجموم','الجموم'),
            ('رابغ','رابغ'),
            ('شرورة','شرورة'),
            ('الليث','الليث'),
            ('رفحاء','رفحاء'),
            ('عفيف','عفيف'),
            ('العرضيات','العرضيات'),
            ('العارضة','العارضة'),
            ('الخفجي','الخفجي'),
            ('بالقرن','بالقرن'),
            ('الدرعية','الدرعية'),
            ('ضمد','ضمد'),
            ('طبرجل','طبرجل'),
            ('بيش','بيش'),
            ('الزلفي','الزلفي'),
            ('الدرب','الدرب'),
            ('الافلاج','الافلاج'),
            ('سراة عبيدة','سراة عبيدة'),
            ('رجال المع','رجال المع'),
            ('بلجرشي','بلجرشي'),
            ('الحائط','الحائط'),
            ('ميسان','ميسان'),
            ('بدر','بدر'),
            ('املج','املج'),
            ('رأس تنوره','رأس تنوره'),
            ('المهد','المهد'),
            ('الدائر','الدائر'),
            ('البكيريه','البكيريه'),
            ('البدائع','البدائع'),
            ('خليص','خليص'),
            ('الحناكية','الحناكية'),
            ('العلا','العلا'),
            ('الطوال','الطوال'),
            ('النماص','النماص'),
            ('المجاردة','المجاردة'),
            ('بقيق','بقيق'),
            ('تثليث','تثليث'),
            ('المخواة','المخواة'),
            ('النعيرية','النعيرية'),
            ('الوجه','الوجه'),
            ('ضباء','ضباء'),
            ('بارق','بارق'),
            ('طريف','طريف'),
            ('خيبر','خيبر'),
            ('أضم','أضم'),
            ('النبهانية','النبهانية'),
            ('رنيه','رنيه'),
            ('دومة الجندل','دومة الجندل'),
            ('المذنب','المذنب'),
            ('تربه','تربه'),
            ('ظهران الجنوب','ظهران الجنوب'),
            ('حوطة بني تميم','حوطة بني تميم'),
            ('الخرمة','الخرمة'),
            ('قلوه','قلوه'),
            ('شقراء','شقراء'),
            ('المويه','المويه'),
            ('المزاحمية','المزاحمية'),
            ('الأسياح','الأسياح'),
            ('بقعاء','بقعاء'),
            ('السليل','السليل'),
            ('تيماء','تيماء')
            ], string='المدينة')    

    
    
class consultingticket(models.Model):
    _inherit = 'consulting.consulting'

    ticket_id = fields.Many2one('helpdesk.ticket', string='التذكرة')
    service_date = fields.Date("الوقت المتوقع لتقديم الخدمة")

    def action_approve(self):
        for consulting in self:
            if consulting.ticket_id:
                ticket_id = self.ticket_id
                stage_id = self.env['helpdesk.stage'].sudo().search([('clf_number','=','5')])
                ticket_id.sudo().stage_id = stage_id
        return super(consultingticket, self).action_approve()
    
    
class createconsultings(models.TransientModel):
    _name = 'create.consultings'
    _description = 'create consultings'

    
    def create_consulting(self):
        values = {
            'name': self.name,
            'project_id': self.project_id.id,
            'partner_id': self.partner_id.id,
            'ticket_id': self.ticket_id.id,
            'company_id': self.company_id,
            'user_id': self.user_id.id,
            'date': self.date,
            'summary': self.summary,
            'consult': self.consult,
            'consulting_type': self.consulting_type,
            'other': self.other,
            'service_date': self.service_date,
        }
        record = self.env['consulting.consulting'].create(values)
        ticket_id = self.ticket_id
        rfq= record.id
        attachment = self.env['ir.attachment'].search([('res_model','=','helpdesk.ticket'), ('res_id','=', ticket_id.id)])
        attachment.write({'res_model': 'consulting.consulting', 'res_id': rfq,})
        messages = self.env['mail.message'].search([('model','=','helpdesk.ticket'), ('res_id','=', ticket_id.id), ('subtype_id.internal','=', False)])
        for message in messages:
            message_values = {
                'model': 'consulting.consulting',
                'res_id': rfq,
                'subject': message.subject,
                'date': message.date,
                'body': message.body,
                'description': message.description,
                'attachment_ids': message.attachment_ids,
                'message_type': message.message_type,
                'subtype_id': message.subtype_id.id,
                'is_internal': message.is_internal,
                'author_id': message.author_id.id,
            }
            new_messages = self.env['mail.message'].create(message_values)
        stage_id = self.env['helpdesk.stage'].sudo().search([('clf_number','=','2')])
        self.ticket_id.write({'stage_id': stage_id.id})

        
    @api.depends('ticket_id')
    def get_description(self):
        if self.ticket_id.description:
            self.summary = self.ticket_id.description
            self.date = self.ticket_id.create_date
            
    ticket_id = fields.Many2one('helpdesk.ticket', string='التذكرة', default=lambda self:self.env['helpdesk.ticket'].search([], limit=1))
    service_date = fields.Date(related='ticket_id.service_date')
    partner_id = fields.Many2one(related='ticket_id.partner_id', string='العميل')
    parent_id = fields.Many2one(related='partner_id.parent_id')
    child_ids = fields.One2many(related='partner_id.child_ids') 
    project_id = fields.Many2one('project.project', string='المشروع')
    name = fields.Char("الاستشارة")
    company_id = fields.Many2one('res.company', related='user_id.company_id', string='Company', required=True)
    user_id = fields.Many2one('res.users', related='project_id.user_id', string='المستشار')
    date = fields.Datetime(string='تاريخ الاستشارة', compute='get_description', readonly=False)
    summary = fields.Text(string='ملخص استشارة العميل', compute='get_description', readonly=True)
    consult = fields.Text(string='الرأي الاستشاري المقترح')
    other = fields.Char(string='اخرى')
    consulting_type = fields.Selection([
            ('استشارة أحوال شخصية', 'استشارة أحوال شخصية'),
            ('دراسة قضية', 'دراسة قضية'),
            ('استشارة تأمينية', 'استشارة تأمينية'),
            ('استشارة مصرفية', 'استشارة مصرفية'),
            ('استشارة تمويلية', 'استشارة تمويلية'),
            ('استشارة جنائية', 'استشارة جنائية'),
            ('استشارة إدارية', 'استشارة إدارية'),
            ('استشارة عمالية', 'استشارة عمالية'),
            ('استشارة تجارية', 'استشارة تجارية'),
            ('استشارة أوقاف', 'استشارة أوقاف'),
            ('استشارة قانونية أخرى', 'استشارة قانونية أخرى')
            ], string='نوع الاستشارة')
    


class contractconsultingticket(models.Model):
    _inherit = 'contractconsulting.contractconsulting'

    ticket_id = fields.Many2one('helpdesk.ticket', string='التذكرة')
    service_date = fields.Date("الوقت المتوقع لتقديم الخدمة")

    def action_approve(self):
        for contractconsulting in self:
            if contractconsulting.ticket_id:
                ticket_id = self.ticket_id
                stage_id = self.env['helpdesk.stage'].sudo().search([('clf_number','=','5')])
                ticket_id.sudo().stage_id = stage_id
        return super(contractconsultingticket, self).action_approve()
    
    
class createcontractconsultings(models.TransientModel):
    _name = 'create.contractconsultings'
    _description = 'create contractconsultings'


    def create_contractconsulting(self):
        values = {
            'name': self.name,
            'project_id': self.project_id.id,
            'partner_id': self.partner_id.id,
            'ticket_id': self.ticket_id.id,
            'company_id': self.company_id,
            'user_id': self.user_id.id,
            'date': self.date,
            'summary': self.summary,
            'draft_contract': self.draft_contract,
            'recommended_contract': self.recommended_contract,
            'sign_contract': self.sign_contract,
            'consulting_type': self.consulting_type,
            'service_date': self.service_date,
        }
        record = self.env['contractconsulting.contractconsulting'].create(values)
        ticket_id = self.ticket_id
        rfq= record.id
        attachment = self.env['ir.attachment'].search([('res_model','=','helpdesk.ticket'), ('res_id','=', ticket_id.id)])
        attachment.write({'res_model': 'contractconsulting.contractconsulting', 'res_id': rfq,})
        messages = self.env['mail.message'].search([('model','=','helpdesk.ticket'), ('res_id','=', ticket_id.id), ('subtype_id.internal','=', False)])
        for message in messages:
            message_values = {
                'model': 'contractconsulting.contractconsulting',
                'res_id': rfq,
                'subject': message.subject,
                'date': message.date,
                'body': message.body,
                'description': message.description,
                'attachment_ids': message.attachment_ids,
                'message_type': message.message_type,
                'subtype_id': message.subtype_id.id,
                'is_internal': message.is_internal,
                'author_id': message.author_id.id,
            }
            new_messages = self.env['mail.message'].create(message_values)
        stage_id = self.env['helpdesk.stage'].sudo().search([('clf_number','=','3')])
        self.ticket_id.write({'stage_id': stage_id.id})

        
    @api.depends('ticket_id')
    def get_description(self):
        if self.ticket_id.description:
            self.summary = self.ticket_id.description
            self.date = self.ticket_id.create_date

    ticket_id = fields.Many2one('helpdesk.ticket', string='التذكرة', default=lambda self:self.env['helpdesk.ticket'].search([], limit=1))
    service_date = fields.Date(related='ticket_id.service_date')
    partner_id = fields.Many2one(related='ticket_id.partner_id', string='العميل')
    parent_id = fields.Many2one(related='partner_id.parent_id')
    child_ids = fields.One2many(related='partner_id.child_ids') 
    project_id = fields.Many2one('project.project', string='المشروع')
    name = fields.Char("استشارة العقد")
    company_id = fields.Many2one('res.company', related='user_id.company_id', string='Company')
    user_id = fields.Many2one('res.users', related='project_id.user_id', string='المستشار')
    date = fields.Datetime(string='تاريخ الاستشارة', compute='get_description', readonly=False)
    summary = fields.Text(string='ملخص الاستشارة', compute='get_description', readonly=True)
    draft_contract = fields.Char(string='مسودة العقد الأولية')
    recommended_contract = fields.Char(string="العقد الموصى به")
    sign_contract = fields.Char(string="العقد الموقع مع العميل")
    consulting_type = fields.Selection([
            ('عقد إيجار التجاري', 'عقد إيجار التجاري'),
            ('عقود العمل ( مدد )', 'عقود العمل ( مدد )'),
            ('عقود الفرنشايز', 'عقود الفرنشايز'),
            ('تأسيس شركة ذات مسؤولية محدودة', 'تأسيس شركة ذات مسؤولية محدودة'),
            ('عقد تأسيس / تحويل إلى شركة مساهمة', 'عقد تأسيس / تحويل إلى شركة مساهمة'),
            ('عقود الآجل ( Credit )', 'عقود الآجل ( Credit )'),
            ('عقد مقاولات', 'عقد مقاولات'),
            ('عقد وساطة وتسويق', 'عقد وساطة وتسويق'),
            ('أخرى', 'أخرى')
            ], string='نوع العقد')

    
    
class HelpdeskStage(models.Model):
    _inherit = 'helpdesk.stage'
        
    clf_number = fields.Integer('رقم المرحلة', default=10)
    un_seen = fields.Boolean('لا تظهر للعميل')
