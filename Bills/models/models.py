# -*- coding: utf-8 -*-
# Copyright to Mutn

from odoo import models, fields, api, _
from odoo.tools.misc import formatLang
from datetime import datetime, timedelta, date


class bills_management(models.Model):
    _name = 'bills.management'
    _description = 'الفواتير'
    _order = 'name'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    
    
    url = fields.Char(compute='get_url')
    
    def get_url(self):
        for bill in self:
            base_url = bill.company_id.website
            bill.url = base_url + '/web#id=' + str(bill.id) + '&model=bills.management&view_type=form'

    name = fields.Char(string="الفاتورة", tracking=True)
    user_id = fields.Many2one(related='employee_id.user_id', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=True, default=lambda self: self.env.user.employee_id, tracking=True)
    company_id = fields.Many2one('res.company', 'الشركة', index=True, default=lambda self: self.env.company, tracking=True)
    expense_amount = fields.Float(string='مبلغ الفاتورة', required=True, tracking=True)
    custody_id = fields.Many2one('custody.management')
    file = fields.Binary('ملف الفاتورة', tracking=True)    
    state = fields.Selection([
        ('draft','مسودة'),
        ('accountant_ap', 'تمت الموافقة من قبل المحاسب'),
        ('hr_ap', 'تمت الموافقة من قبل الموارد البشرية'),
        ('admin_ap','معتمد'),
        ('paid','مسدد'),
    ], required=True, default='draft', string='الحالة', tracking=True)
    bills_state = fields.Selection([
        ('custody','فاتورة عهدة'),
        ('employee', 'فاتورة موظف'),
        ], string='النوع', compute="_get_bills_state", store=True)
    
    @api.depends('custody_id') 
    def _get_bills_state(self):
        for bill in self:
            bills_state = 'employee'
            if bill.custody_id:
                bills_state = 'custody'
            bill.bills_state = bills_state

    note = fields.Text('ملاحظات', tracking=True)    
    bank = fields.Binary('الحوالة البنكية', tracking=True)    

    def action_accountant_approve(self):
        self.sudo().write({'state':'accountant_ap'})
       
    def action_hr_approve(self):
        self.sudo().write({'state':'hr_ap'})
        
    def action_admin_approve(self):
        self.sudo().write({'state':'admin_ap'})

    def action_paid(self):
        self.sudo().write({'state':'paid'})
        
    def action_draft(self):
        self.sudo().write({'state':'draft'})

class custody_management(models.Model):
    _name = 'custody.management'
    _description = 'العهدة المالية'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(string="العهدة المالية", tracking=True)
    user_id = fields.Many2one(related='employee_id.user_id', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=True, default=lambda self: self.env.user.employee_id, tracking=True)
    bills_ids = fields.One2many('bills.management', 'custody_id', string='الفواتير', tracking=True)
    company_id = fields.Many2one('res.company', 'الشركة', index=True, default=lambda self: self.env.company, tracking=True)
    date_custody= fields.Date("التاريخ", tracking=True)
    job_position = fields.Char(string="المسمى الوظيفي", tracking=True)
    sign = fields.Binary(string="التوقيع", tracking=True)
    custody = fields.Float(string="المبلغ", tracking=True)
    iban = fields.Char(string="رقم حساب (الآيبان)", tracking=True)
    back = fields.Date(string='تاريخ اخلاء الطرف', tracking=True)
    state = fields.Selection([
        ('draft','مسودة'),
        ('approval', 'تمت الموافقة'),
        ('admin_ap','معتمد'),
        ('done_request', 'طلب إخلاء طرف'),
        ('done', 'إخلاء طرف'),
        ], required=True, default='draft', string='الحالة', tracking=True)
    custody_remaining = fields.Float(string="المبلغ المتبقي", compute="_get_custody_remaining", tracking=True)
    
    def _get_custody_remaining(self):
        for custody in self:
            custody_remaining = 0.0
            amount = 0.0
            company = 'الشركة'
            if custody.bills_ids:
                for bill in custody.bills_ids:
                    amount += bill.expense_amount
            custody_remaining = custody.custody - amount
            custody.custody_remaining = custody_remaining

    note = fields.Text(string="إقرار", compute="get_note")

    def get_note(self):
        for custody in self:
            money = 0.0
            company = 'الشركة'
            if custody.custody:
                money = custody.custody
            if custody.company_id.name:
                company = custody.company_id.name
            note = ('أقر أني الموقع أدناه بأني استلمت العهدة الموضحة لبياناتي أعلاه بمبلغ ' + str(money) + ' ريال وذلك عهدة للصرف على أعمال مقر ' + company + '\n' + 'ملحوظة:' + '\n' 
            + 'يلزم عدم إخلاء طرف مستلم العهدة إلى أن يرفق ما يثبت خلو طرفه بخصوص العهدة (إما تسديدها بالفواتير أو نقلها إلى موظف أخر) .')
            custody.note = note
            
    def done_request_action(self):
        for custody in self:
            local_context = dict(
                self.env.context,
                default_custody_id= custody.id,
            )
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_id': self.env.ref('Bills.custody_done_request_form').id,
                'res_model': 'asset.donerequest',
                'target': 'new',
                'context': local_context,
            }

    def action_hr_approve(self):
        self.sudo().write({'state':'approval'})
        
    def action_admin_approve(self):
        self.sudo().write({'state':'admin_ap'})

    def action_draft(self):
        self.sudo().write({'state':'draft'})
        
    def action_done(self):
        self.sudo().write({'state':'done'})
        
        
class account_asset(models.Model):
    _inherit = "account.asset"
    
    employees_asset_custody = fields.One2many('asset.custody', 'asset_id', string='العهدة')
    s_number = fields.Char(string='الرقم التسلسلي')
    
    

class assetcustody(models.Model):
    _name = 'asset.custody'
    _description = 'العهدة العينية'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    name = fields.Char(string="العهدة", tracking=True)
    asset_id = fields.Many2one('account.asset', 'نوع العهدة', tracking=True)
    user_id = fields.Many2one(related='employee_id.user_id', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=True, default=lambda self: self.env.user.employee_id, tracking=True)
    company_id = fields.Many2one('res.company', 'الشركة', index=True, default=lambda self: self.env.company, tracking=True)
    recived = fields.Date(string='تاريخ استلام العهدة', tracking=True)
    back = fields.Date(string='تاريخ اخلاء الطرف', tracking=True)
    back_state = fields.Char(string='حالة العهدة عند اخلاء الطرف', tracking=True)
    job_position = fields.Char(string="المنصب الوظيفي", tracking=True)
    sign = fields.Binary(string="التوقيع", tracking=True)
    asset_value = fields.Monetary(string="قيمة العهدة", currency_field='company_currency', related='asset_id.original_value', tracking=True)
    company_currency = fields.Many2one(related='company_id.currency_id', tracking=True)
    state = fields.Selection([
        ('draft','مسودة'),
        ('approval', 'تمت الموافقة'),
        ('admin_ap','معتمد'),
        ('done_request', 'طلب إخلاء طرف'),
        ('done', 'إخلاء طرف'),
        ], required=True, default='draft', string='الحالة', tracking=True)
  
    note = fields.Text(string="إقرار", compute="get_note")

    def get_note(self):
        for custody in self:
            asset = '....'
            asset_value = 0.0
            company = 'الشركة'
            if custody.asset_id:
                asset = custody.asset_id.name
            if custody.asset_value:
                asset_value = formatLang(self.env, custody.asset_value)
            note = ('أقر أني الموقع أدناه بأني استلمت العهدة ' + asset + ' الموضحة لبياناتي أعلاه وقيمتها ' + str(asset_value) + ' وذلك كعهدة لاستخدامها في أعمال الشركة ، و أتعهد بالمحافظة عليها و اعادة تسليمها للشركة لدى انتهاء الغرض من استخدامها أو لدى تركي العمل بالشركة. و في حالة عدم تسليم العهدة المذكورة أعلاه ، كلها أو بعضها فأنني أفوض الشركة في اتخاذ اللازم نحو خصم القيمة التي تقدرها مقابل هذه العهدة، من مستحقاتي لديها ، دون أى اعتراض مني. ' + '\n' + 'ملحوظة:' + '\n' 
            + 'يلزم عدم إخلاء طرف مستلم العهدة إلى أن يرفق ما يثبت خلو طرفه بخصوص العهدة (إما بتسليمها أو نقلها إلى موظف أخر) .')            
            custody.note = note
            
    def done_request_action(self):
        for custody in self:
            local_context = dict(
                self.env.context,
                default_asset_custody_id= custody.id,
            )
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_id': self.env.ref('Bills.asset_done_request_form').id,
                'res_model': 'asset.donerequest',
                'target': 'new',
                'context': local_context,
            }

    def action_hr_approve(self):
        self.sudo().write({'state':'approval'})
        
    def action_admin_approve(self):
        self.sudo().write({'state':'admin_ap'})

    def action_draft(self):
        self.sudo().write({'state':'draft'})
        
    def action_done(self):
        self.sudo().write({'state':'done'})
        
        
class AssetCustody(models.TransientModel):
    _name = 'asset.donerequest'
    _description = 'اخلاء طرف'

    def donerequest(self):
        for donerequest in self:
            if donerequest.asset_custody_id:                
                donerequest.asset_custody_id.back = donerequest.back
                donerequest.asset_custody_id.back_state = donerequest.back_state
                donerequest.asset_custody_id.state = 'done_request'
            if donerequest.custody_id:                
                donerequest.asset_custody_id.back = donerequest.back
                donerequest.asset_custody_id.state = 'done_request'


    asset_custody_id = fields.Many2one('asset.custody', auto_join=True)
    custody_id = fields.Many2one('custody.management', auto_join=True)
    back = fields.Date(string='تاريخ اخلاء الطرف', default=date.today())
    back_state = fields.Char(string='حالة العهدة عند اخلاء الطرف')