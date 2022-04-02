# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning
from datetime import datetime
import uuid

class balaghs(models.Model):
    _name = 'balagh.balagh'
    _description = 'بلاغ'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    def _default_access_token(self):
        return str(uuid.uuid4())
    
    access_token = fields.Char('Security Token', required=True, default=_default_access_token, readonly=True)

    url = fields.Char(compute='get_url')
    
    def get_url(self):
        base_url = self.company_id.website
        self.url = base_url + '/web#id=' + str(self.id) + '&model=balagh.balagh&view_type=form'


    
    def action_send(self):
        for slate in self:
            slate.write({'state': 'يتم الإرسال'})
            return True

    def action_submit(self):
        for slate in self:
            slate.write({'state': 'تم التبليغ'})
            return True

    def action_fail(self):
        for slate in self:
            slate.write({'state': 'تعذر التبليغ'})
            return True

    def action_draft(self):
        for slate in self:
            slate.write({'state': 'جديد'})
            return True

    state = fields.Selection([
        ('جديد', 'جديد'),
        ('يتم الإرسال', 'يتم الإرسال'),
        ('تعذر التبليغ', 'تعذر التبليغ'),
        ('تم التبليغ', 'تم التبليغ'),
        ], string='الحالة', default='جديد')
    name = fields.Char(string="الإسم")
    partner_id = fields.Many2one('res.partner', string='العميل', auto_join=True, tracking=True, required=True)
    balagh_id = fields.Many2one('balagh.messages', string='الرسالة التبليغية', required=True)
    variables = fields.Selection(related='balagh_id.variables')
    user_id = fields.Many2one('res.users', string='المسؤول', related='balagh_id.user_id')
    company_id = fields.Many2one(related='user_id.company_id')
    message = fields.Text(string="الرسالة", compute='get_message')
    variable_1 = fields.Char(string="المتغير الأول")
    variable_2 = fields.Char(string="المتغير الثاني")
    variable_3 = fields.Char(string="المتغير الثالث")
    variable_4 = fields.Char(string="المتغير الرابع")
    variable_5 = fields.Char(string="المتغير الخامس")
    variable_6 = fields.Char(string="المتغير السادس")
    variable_7 = fields.Char(string="المتغير السابع")
    variable_8 = fields.Char(string="المتغير الثامن")
    recever_id = fields.Char(string="هوية المرسل إليه")
    recever_name = fields.Char(string="اسم المرسل إليه")
    sender_name = fields.Char(string="اسم المرسل")
    price = fields.Float(string="سعر الرسالة", compute='price_default', store=True, readonly=False)
    qutation_id = fields.Many2one('sale.order', string='عرض السعر', readonly=True)
    order_name = fields.Char(string="رقم طلب الإشعار")
    order_file = fields.Binary(string="التقرير")

    @api.constrains('variable_1','variable_2','variable_3','variable_4','variable_5','variable_6','variable_7','variable_8')
    def _check_variable(self):
        for balagh in self:
            variable_1 = balagh.variable_1
            variable_2 = balagh.variable_2
            variable_3 = balagh.variable_3
            variable_4 = balagh.variable_4
            variable_5 = balagh.variable_5
            variable_6 = balagh.variable_6
            variable_7 = balagh.variable_7
            variable_8 = balagh.variable_8
            if variable_1:
                if len(variable_1) > 49:
                    raise ValidationError(_('المتغير الأول تجاوز عدد الحروف المسموحة (49 حرف)'))    
                if ',' in variable_1 or '،' in variable_1 or ';' in variable_1 or '’' in variable_1 or '؛'  in variable_1:
                    raise ValidationError(_('الفواصل غير مسموحة (في المتغير الأول)'))
            if variable_2:
                if len(variable_2) > 49:
                    raise ValidationError(_('المتغير الثاني تجاوز عدد الحروف المسموحة (49 حرف)'))    
                if ',' in variable_2 or '،' in variable_2 or ';' in variable_2 or '’' in variable_2 or '؛'  in variable_2:
                    raise ValidationError(_('الفواصل غير مسموحة (في المتغير الثاني)'))
            if variable_3:
                if len(variable_3) > 49:
                    raise ValidationError(_('المتغير الثالث تجاوز عدد الحروف المسموحة (49 حرف)'))    
                if ',' in variable_3 or '،' in variable_3 or ';' in variable_3 or '’' in variable_3 or '؛'  in variable_3:
                    raise ValidationError(_('الفواصل غير مسموحة (في المتغير الثالث)'))
            if variable_4:
                if len(variable_4) > 49:
                    raise ValidationError(_('المتغير الرابع تجاوز عدد الحروف المسموحة (49 حرف)'))    
                if ',' in variable_4 or '،' in variable_4 or ';' in variable_4 or '’' in variable_4 or '؛'  in variable_4:
                    raise ValidationError(_('الفواصل غير مسموحة (في المتغير الرابع)'))
            if variable_5:
                if len(variable_5) > 49:
                    raise ValidationError(_('المتغير الخامس تجاوز عدد الحروف المسموحة (49 حرف)'))    
                if ',' in variable_5 or '،' in variable_5 or ';' in variable_5 or '’' in variable_5 or '؛'  in variable_5:
                    raise ValidationError(_('الفواصل غير مسموحة (في المتغير الخامس)'))
            if variable_6:
                if len(variable_6) > 49:
                    raise ValidationError(_('المتغير السادس تجاوز عدد الحروف المسموحة (49 حرف)'))    
                if ',' in variable_6 or '،' in variable_6 or ';' in variable_6 or '’' in variable_6 or '؛'  in variable_6:
                    raise ValidationError(_('الفواصل غير مسموحة (في المتغير السادس)'))
            if variable_7:
                if len(variable_7) > 49:
                    raise ValidationError(_('المتغير السادس تجاوز عدد الحروف المسموحة (49 حرف)'))    
                if ',' in variable_7 or '،' in variable_7 or ';' in variable_7 or '’' in variable_7 or '؛'  in variable_7:
                    raise ValidationError(_('الفواصل غير مسموحة (في المتغير السادس)'))
            if variable_8:
                if len(variable_8) > 49:
                    raise ValidationError(_('المتغير الثامن تجاوز عدد الحروف المسموحة (49 حرف)'))
                if ',' in variable_8 or '،' in variable_8 or ';' in variable_8 or '’' in variable_8 or '؛'  in variable_8:
                    raise ValidationError(_('الفواصل غير مسموحة (في المتغير الثامن)'))
                                

    @api.depends('balagh_id')
    def price_default(self):
        for balagh in self:
            if balagh.balagh_id:
                balagh.price = balagh.balagh_id.price

    @api.model_create_multi
    def create(self, vals_list):
        record = super(balaghs, self).create(vals_list)
        if record.name:
            record.name = record.name + (" بلاغ #%s" % (record.id))
        else:
            record.name = (" بلاغ #%s" % (record.id))
        if record.user_id != self.env.user:
            mail_template = self.env.ref('balagh.send_email_balagh')
            mail_template.send_mail(record.id, force_send=True,notif_layout='mail.mail_notification_light')
                        
#         product_id = self.env['product.product'].search([('name', '=', 'رسالة بلاغية')], limit=1)
#         vals = [{
#             'name': record.name,
#             'partner_id': record.partner_id.id,
#             'user_id': record.user_id.id,
#             'sale_type': 'اخرى',
#             'payment_term_note': 'كامل المبلغ مقدما',
#             'state': 'sent',
#             }]
#         qutation_id = self.env['sale.order'].sudo().create(vals)
#         line = [{
#             'name': record.name,
#             'product_id': product_id.id,
#             'price_unit': record.price,
#             'order_id': qutation_id.id,
#             'product_uom_qty': 1.0,
#             'qty_delivered': 1.0,
#             }]
#         self.env['sale.order.line'].sudo().create(line)
#         record.qutation_id = qutation_id.id
        return record                
                
    @api.depends('variable_1','variable_2','variable_3','variable_4','variable_5','variable_6','variable_7','variable_8')
    def get_message(self):
        message = ''
        for balagh in self:
            if balagh.balagh_id.variables == '1':
                if balagh.variable_1:
                    message = balagh.balagh_id.message.replace('#1', balagh.variable_1)
            elif balagh.balagh_id.variables == '2':
                if balagh.variable_1 and balagh.variable_2:
                    message = balagh.balagh_id.message.replace('#2', balagh.variable_2).replace('#1', balagh.variable_1)
            elif balagh.balagh_id.variables == '3':
                if balagh.variable_1 and balagh.variable_2 and balagh.variable_3:
                    message = balagh.balagh_id.message.replace('#3', balagh.variable_3).replace('#2', balagh.variable_2).replace('#1', balagh.variable_1)
            elif balagh.balagh_id.variables == '4':
                if balagh.variable_1 and balagh.variable_2 and balagh.variable_3 and balagh.variable_4:
                    message = balagh.balagh_id.message.replace('#4', balagh.variable_4).replace('#3', balagh.variable_3).replace('#2', balagh.variable_2).replace('#1', balagh.variable_1)
            elif balagh.balagh_id.variables == '5':
                if balagh.variable_1 and balagh.variable_2 and balagh.variable_3 and balagh.variable_4 and balagh.variable_5:
                    message = balagh.balagh_id.message.replace('#5', balagh.variable_5).replace('#4', balagh.variable_4).replace('#3', balagh.variable_3).replace('#2', balagh.variable_2).replace('#1', balagh.variable_1)
            elif balagh.balagh_id.variables == '6':
                if balagh.variable_1 and balagh.variable_2 and balagh.variable_3 and balagh.variable_4 and balagh.variable_5 and balagh.variable_6:
                    message = balagh.balagh_id.message.replace('#6', balagh.variable_6).replace('#5', balagh.variable_5).replace('#4', balagh.variable_4).replace('#3', balagh.variable_3).replace('#2', balagh.variable_2).replace('#1', balagh.variable_1)
            elif balagh.balagh_id.variables == '7':
                if balagh.variable_1 and balagh.variable_2 and balagh.variable_3 and balagh.variable_4 and balagh.variable_5 and balagh.variable_6 and balagh.variable_7:
                    message = balagh.balagh_id.message.replace('#7', balagh.variable_7).replace('#6', balagh.variable_6).replace('#5', balagh.variable_5).replace('#4', balagh.variable_4).replace('#3', balagh.variable_3).replace('#2', balagh.variable_2).replace('#1', balagh.variable_1)
            elif balagh.balagh_id.variables == '8':
                if balagh.variable_1 and balagh.variable_2 and balagh.variable_3 and balagh.variable_4 and balagh.variable_5 and balagh.variable_6 and balagh.variable_7 and balagh.variable_8:
                    message = balagh.balagh_id.message.replace('#8', balagh.variable_8).replace('#7', balagh.variable_7).replace('#6', balagh.variable_6).replace('#5', balagh.variable_5).replace('#4', balagh.variable_4).replace('#3', balagh.variable_3).replace('#2', balagh.variable_2).replace('#1', balagh.variable_1)
                    
            balagh.message = message
            


class balaghmessages(models.Model):
    _name = 'balagh.messages'
    _description = 'رسائل بلاغ'
    
    name = fields.Char(string="الإسم")
    user_id = fields.Many2one('res.users', string='المسؤول', default=lambda self: self.env.user, required=True)
    message = fields.Text(string="الرسالة", default='سعادة #1 هذه الرسالة تبليغية بشأن #2 مرسلة من قبل #3')
    variables = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ], default='1', string="عدد المتغيرات")
    price = fields.Float(string="سعر الرسالة")