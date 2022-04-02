# Copyright to Mutn

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import uuid


class birkman_serivce_type(models.Model):
    _name = 'birkman.serivce.type'
    _description = 'باقات بيركمان'

    name = fields.Char(string="الاسم")
    price = fields.Float(string="السعر")
    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company, required=True)
    company_currency = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id', readonly=True)
    user_id = fields.Many2one('res.users', string='المسؤول', default=lambda self: self.env.user, required=True)
    description = fields.Char(string="الوصف")
    price_value = fields.Char(string="بديل السعر")

class birkman(models.Model):
    _name = 'birkman'
    _description = 'بيركمان'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    
    
    def _default_access_token(self):
        return str(uuid.uuid4())

    access_token = fields.Char('Security Token', required=True, default=_default_access_token, readonly=True)
    
    
    url = fields.Char(compute='get_url')
    
    def get_url(self):
        base_url = self.company_id.website
        self.url = base_url + '/web#id=' + str(self.id) + '&model=birkman&view_type=form'

        
    portal_url = fields.Char(compute='get_portal_url')
    
    def get_portal_url(self):
        base_url = self.company_id.website
        self.portal_url = base_url + '/my/birkman/' + str(self.id) + '?access_token=' + self.access_token
        
        
    sale_url = fields.Char(compute='get_sale_url')
    
    def get_sale_url(self):
        sale_url = False
        if self.qutation_id:
            base_url = self.company_id.website
            sale_url = base_url + '/my/orders/' + str(self.qutation_id.id) + '?access_token=' + self.qutation_id.access_token
        self.sale_url = sale_url

        
    def action_review(self):
        for birkman in self:
            birkman.write({'state': 'في حالة المراجعة'})
            return True

    def action_submit(self):
        for birkman in self:
            birkman.write({'state': 'معتمد'})
            return True

    def action_draft(self):
        for birkman in self:
            birkman.write({'state': 'جديد'})
            return True

    state = fields.Selection([
        ('جديد', 'جديد'),
        ('في حالة المراجعة', 'في حالة المراجعة'),
        ('معتمد', 'معتمد'),
        ], string='الحالة', default='جديد')
    name = fields.Char(string="الاسم")
    qutation_id = fields.Many2one('sale.order', string='عرض السعر', readonly=True)
    service_type_id = fields.Many2one('birkman.serivce.type', string='نوع الباقة', required=True)
    partner_id = fields.Many2one('res.partner', string='العميل', auto_join=True)
    partner = fields.Char(related='partner_id.name', string='اسم العميل')
    user_id = fields.Many2one(related='service_type_id.user_id')
    company_id = fields.Many2one(related='service_type_id.company_id')
    phone = fields.Char(related='partner_id.phone', string='الجوال', readonly=False)
    email = fields.Char(related='partner_id.email', string='البريد الإلكتروني', readonly=False)
    qty = fields.Float(string='عدد المختبرين', default=1.0)
    
    
    @api.model_create_multi
    def create(self, vals_list):
        record = super(birkman, self).create(vals_list)
        if record.partner_id:
            record.name = 'اختبار بيركمان ل' + str(record.partner_id.name)         
        
        product_id = self.env['product.product'].sudo().search([('name', '=', 'اختبار بيركمان')], limit=1)
        vals = [{
            'name': record.name,
            'partner_id': record.partner_id.id,
            'user_id': record.user_id.id,
            'sale_type': 'اخرى',
            'payment_term_note': 'كامل المبلغ مقدما',
            'state': 'sent',
            }]
        qutation_id = self.env['sale.order'].sudo().create(vals)
        line = [{
            'name': record.service_type_id.name,
            'product_id': product_id.id,
            'price_unit': record.service_type_id.price,
            'order_id': qutation_id.id,
            'product_uom_qty': record.qty,
            'qty_delivered': 1.0,
            }]
        self.env['sale.order.line'].sudo().create(line)
        record.qutation_id = qutation_id.id
        if record.user_id != self.env.user:
            mail_template = self.env.ref('birkman.new_birkman_email_template')
            mail_template.send_mail(record.id, force_send=True,notif_layout='mail.mail_notification_light')        
        return record