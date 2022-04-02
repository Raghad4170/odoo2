# -*- coding: utf-8 -*-

import ast
from datetime import timedelta, datetime, date
from random import randint
import uuid
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning
from odoo.tools.misc import format_date, get_lang
from odoo.osv.expression import OR
from odoo.modules.module import get_module_resource
import base64


class estate(models.Model):
    _name = 'estate.estate'
    _description = 'estate.estate'
    _order = 'id'
    
    name = fields.Char("العقارات")
    partner_id = fields.Many2one('res.partner', string='العميل', auto_join=True)
    partner_employee = fields.Many2one('res.partner', string='موظف العميل', auto_join=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='مسؤول العقد', default=lambda self: self.env.user)
    building_ids = fields.One2many('building.building', 'estate_id', string='المبنى')
    contract_ids = fields.One2many('contract.contract', 'estate_id', string='العقد')
    note = fields.Text(string='ملاحظات')
    client_type = fields.Selection([
        ('مُؤجِر', 'مُؤجِر'),
        ('مُستأجِر', 'مُستأجِر')
        ], string='نوع العميل', store=True, copy=False, readonly=False)

            
class building(models.Model):
    _name = 'building.building'
    _description = 'building'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = 'id'

    
    def _default_access_token(self):
        return str(uuid.uuid4())

    access_token = fields.Char('Security Token', required=True, default=_default_access_token, readonly=True)

    def _compute_unit_count(self):
        unit_data = self.env['unit.unit'].read_group([('building_id', 'in', self.ids)], ['building_id'], ['building_id'])
        result = dict((data['building_id'][0], data['building_id_count']) for data in unit_data)
        for building in self:
            building.unit_count = result.get(building.id, 0)
            
    @api.model
    def _default_image(self):
        image_path = get_module_resource('estate', 'views', 'building.png')
        return base64.b64encode(open(image_path, 'rb').read())
   
            
    name = fields.Char("المبنى", tracking=True, required=True)
    image_10 = fields.Image(default=_default_image)
    estate_id = fields.Many2one('estate.estate', string='العقارات', auto_join=True, tracking=True)
    partner_id = fields.Many2one(related='estate_id.partner_id', string='العميل')
    partner_employee = fields.Many2one(related='estate_id.partner_employee')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    company_currency = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id', readonly=True)
    user_id = fields.Many2one(related='estate_id.user_id')
    unit_ids = fields.One2many('unit.unit', 'building_id', string='الوحدة الإيجارية')
    note = fields.Text(string='ملاحظات')
    unit_count = fields.Integer(compute='_compute_unit_count', string="Unit Count")
    contracts_count = fields.Integer(compute='_compute_contract_count', string="Contract Count")
    start_date = fields.Date(string='بداية الإيجار', index=True, required=True)
    end_date = fields.Date(string='نهاية الإيجار', index=True, required=True)
    file = fields.Binary(string='صك الملكية')
    
    def _compute_contract_count(self):
        for building in self:
            # For contracts_count
            contracts_count = 0
            for unit in building.unit_ids:
                contracts_count += unit.contract_count
            building.contracts_count = contracts_count

    # profit total
    profit_total = fields.Float(string='القيمة الفعلية للربح', compute="_compute_total", digits=(12,2))
    # lost totall
    lost_total = fields.Float(string='القيمة التقديرية للخسارة', compute="_compute_total", digits=(12,2))
    # net totall
    net_total = fields.Float(string='صافي الربح', compute="_compute_total", digits=(12,2))
    
    def _compute_total(self):
        for building in self:
            # For profit_total
            profit_total = 0
            for unit in building.unit_ids:
                profit_total += unit.profit_total
            building.profit_total = profit_total
            
            # For lost_total
            lost_total = 0
            for unit in building.unit_ids:
                lost_total += unit.lost_total
            building.lost_total = lost_total

            # For net_total
            net_total = 0
            if building.profit_total and building.lost_total:
                building.net_total = building.profit_total - building.lost_total
            else:
                building.net_total = False

            
    paid_amount = fields.Float(string='مجموع المبالغ المدفوعة', compute='_paid_amount', digits=(12,2))
    amount_left = fields.Float(string='المبالغ المتبقية', compute='_amount_left', digits=(12,2))
    taxs = fields.Float(string='مبلغ الضريبة المضافة', compute='_paid_taxs', digits=(12,2))
    amount_taxed = fields.Float(string='المبلغ الإجمالي', compute='_amount_taxed', digits=(12,2))

    def _paid_taxs(self):
        for building in self:
            taxs = 0
            for unit in building.unit_ids:
                taxs += unit.taxs
            building.taxs = taxs
            
    def _amount_taxed(self):
        for building in self:
            building.amount_taxed = building.taxs + building.paid_amount
            
    def _paid_amount(self):
        for building in self:
            paid_amount = 0
            for unit in building.unit_ids:
                paid_amount += unit.paid_amount
            building.paid_amount = paid_amount
            
    def _amount_left(self):
        for building in self:
            amount_left = 0
            for unit in building.unit_ids:
                amount_left += unit.amount_left
            building.amount_left = amount_left
            
class unit(models.Model):
    _name = 'unit.unit'
    _description = 'unit'
    _inherit = []
    _order = 'sequence, id'

    def _compute_contract_count(self):
        contract_data = self.env['contract.contract'].read_group([('unit_id', 'in', self.ids)], ['unit_id'], ['unit_id'])
        result = dict((data['unit_id'][0], data['unit_id_count']) for data in contract_data)
        for unit in self:
            unit.contract_count = result.get(unit.id, 0)
                       
    name = fields.Char("الوحدة الإيجارية")
    sequence = fields.Integer(default=10, help="Gives the sequence order when displaying a list.")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    company_currency = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id', readonly=True)
    user_id = fields.Many2one(related='building_id.user_id')
    space = fields.Integer(string='مساحة الوحدة بالمتر', index=True)
    building_id = fields.Many2one('building.building', string='المبنى', auto_join=True)
    estate_id = fields.Many2one(related='building_id.estate_id')
    partner_id = fields.Many2one('res.partner', related='building_id.partner_id', string='العميل', auto_join=True)
    partner_employee = fields.Many2one(related='building_id.partner_employee')
    contract_ids = fields.One2many('contract.contract', 'unit_id', string='العقد')
    contract_count = fields.Integer(compute='_compute_contract_count', string="Contract Count")
    note = fields.Text(string='ملاحظات')

    # Field to count the days from 'start_date' untill today
    unitll_today = fields.Float(string='إلى اليوم', compute="_compute_days")
    # Sum the days of all 'contract_ids' from 'count_days'
    rented_day = fields.Float(string='الفترات المؤجرة', compute="_compute_days", digits=(12,2))
    # Subtract the days from 'untill_today' and 'rented_days'
    unrented_days = fields.Float(string='الفترات الغير مؤجرة', compute="_compute_days", digits=(12,2))
    avalibale_days = fields.Float(string='الفترات التأجيرية المتاحة', compute="_compute_days", digits=(12,2))

    
    def _compute_days(self):
        for unit in self:
            unitll_today = 0
            if unit.building_id.start_date:
                unitll_today = (date.today() - unit.building_id.start_date).days
                unit.unitll_today = unitll_today
            else:
                unit.unitll_today = False

            # For rented_day
            rented_day = 0
            for contract in unit.contract_ids:
                rented_day += contract.count_days
            unit.rented_day = rented_day

            # For unrented_days
            if unit.rented_day and unit.building_id.start_date:
                days_left = (date.today() - unit.building_id.start_date).days
                unrented_days = days_left - unit.rented_day
                if unrented_days <= 0:
                    unrented_days = 0
                unit.unrented_days = unrented_days
            else:
                unit.unrented_days = False
                
            # For avalibale_days
            if unit.building_id.end_date:
                avalibale_days = 0
                last_contract = self.env['contract.contract'].sudo().search([('unit_id', '=', unit.id),
                                                                             ('end_date', '>', date.today())], order='end_date desc', limit=1)
                if last_contract:
                    avalibale_days = (unit.building_id.end_date - last_contract.end_date).days
                else:
                    avalibale_days = (unit.building_id.end_date - date.today()).days
                unit.avalibale_days = avalibale_days
            else:
                unit.avalibale_days = False

    # profit total
    profit_total = fields.Float(string='القيمة الفعلية للربح', compute="_compute_profit", digits=(12,2))
    # total meter price
    total_meter = fields.Float(string='مجموع سعر المتر', compute="_compute_total", digits=(12,2))
    # Average meter price
    average_meter = fields.Float(string='متوسط سعر المتر', compute="_compute_average", digits=(12,2))
    # lost totall
    lost_total = fields.Float(string='القيمة التقديرية للخسارة', compute="_compute_lost", digits=(12,2))
    # net totall
    net_total = fields.Float(string='صافي الربح', compute="_compute_net", digits=(12,2))
        
    def _compute_profit(self):
        for unit in self:
            profit_total = 0
            for contract in unit.contract_ids:
                profit_total += contract.rent_amount
            unit.profit_total = profit_total

    def _compute_total(self):
        for unit in self:
            total_meter = 0
            for contract in unit.contract_ids:
                total_meter += contract.price_day
            unit.total_meter = total_meter

    def _compute_average(self):
        for unit in self:
            if unit.total_meter and unit.contract_count:
                unit.average_meter = (unit.total_meter) / (unit.contract_count or 1)
            else:
                unit.average_meter = 0

    def _compute_lost(self):
        for unit in self:
            if unit.average_meter and unit.unrented_days > 0:
                unit.lost_total = unit.average_meter * unit.unrented_days
            else:
                unit.lost_total = 0

    def _compute_net(self):
        for unit in self:
            if unit.profit_total and unit.lost_total:
                unit.net_total = unit.profit_total - unit.lost_total
            else:
                unit.net_total = 0

    paid_amount = fields.Float(string='مجموع المبالغ المدفوعة', compute='_paid_amount', digits=(12,2))
    amount_left = fields.Float(string='المبالغ المتبقية', compute='_amount_left', digits=(12,2))
    taxs = fields.Float(string='مبلغ الضريبة المضافة', compute='_paid_taxs', digits=(12,2))
    amount_taxed = fields.Float(string='المبلغ الإجمالي', compute='_amount_taxed', digits=(12,2))
    
    def _paid_amount(self):
        for unit in self:
            paid_amount = 0
            for contract in unit.contract_ids:
                paid_amount += contract.paid_amount
            unit.paid_amount = paid_amount
            
    def _paid_taxs(self):
        for unit in self:
            taxs = 0
            for contract in unit.contract_ids:
                taxs += contract.taxs
            unit.taxs = taxs
            
    def _amount_taxed(self):
        for unit in self:
            unit.amount_taxed = unit.taxs + unit.paid_amount

    def _amount_left(self):
        for unit in self:
            amount_left = 0
            for contract in unit.contract_ids:
                amount_left += contract.amount_left
            unit.amount_left = amount_left

    
class contract(models.Model):
    _name = 'contract.contract'
    _description = 'contract'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.activity.mixin', 'rating.mixin']
    _order = 'id'
    
    def _default_access_token(self):
        return str(uuid.uuid4())

    access_token = fields.Char('Security Token', required=True, default=_default_access_token, readonly=True)
    
    def _meter_space(self):
        for contract in self:
            difference_in_years = relativedelta(contract.end_date, contract.start_date).years
            rent_amount = (contract.rent_amount or 0.0) / (difference_in_years or 1)
            meter_price = rent_amount / (contract.unit_id.space or 1)    
            contract.meter_price = rent_amount / (meter_price or 1)

    name = fields.Char("عقد الإيجار", tracking=True)
    estate_id = fields.Many2one(related='unit_id.estate_id')
    partner_id = fields.Many2one('res.partner', related='estate_id.partner_id', string='العميل', auto_join=True, tracking=True)
    partner_employee = fields.Many2one(related='estate_id.partner_employee')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    user_id = fields.Many2one(related='unit_id.user_id')
    unit_id = fields.Many2one('unit.unit', string='الوحدة الإيجارية', auto_join=True, tracking=True)
    building_id = fields.Many2one('building.building', related='unit_id.building_id', string='المبنى', auto_join=True, tracking=True)
    payment_ids = fields.One2many('payment.payment', 'contract_id', string='سجل الدفعات')
    start_date = fields.Date(string='بداية الإيجار', index=True)
    end_date = fields.Date(string='نهاية الإيجار', index=True)
    rent_amount = fields.Float(string='قيمة الإيجار', store=True, digits=(12,2))
    meter_price = fields.Float(string='سعر المتر بالريال', compute='_meter_space', tracking=5, digits=(12,2))
    company_currency = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id', readonly=True)
    payment_date = fields.Selection([
        ('شهري', 'شهري'),
        ('ربعي', 'ربعي'),
        ('نصفي', 'نصفي'),
        ('سنوي', 'سنوي')
        ], string='مواعيد السداد', store=True, copy=False, readonly=False)
    terms = fields.Text(string='شروط عقد الإيجار')
    contract_type = fields.Boolean(string='العقد إلكتروني', store=True, copy=False, readonly=False)
    contract_state = fields.Selection([
        ('جديد', 'جديد'),
        ('ساري', 'ساري'),
        ('منتهي', 'منتهي')
        ], string='حالة العقد', store=True, copy=False, readonly=False, compute='_contract_state')
    start_date = fields.Date(string='بداية الإيجار', index=True, required=True)
    end_date = fields.Date(string='نهاية الإيجار', index=True, required=True)
    file = fields.Binary(string='العقد الإلكتروني')
    count_days = fields.Float(string='مدة الإيجار بالأيام', compute='_count_days', index=True, digits=(12,2))
    today = fields.Date(compute='_get_today')
    
    def _get_today(self):
        for contract in self:
            contract.today = date.today() 
            
    @api.depends('start_date', 'end_date', 'today')
    def _contract_state(self):
        for contract in self:
            if contract.start_date and contract.end_date:
                if contract.start_date <= contract.today and contract.end_date >= contract.today:
                    contract.contract_state = 'ساري'
                elif contract.start_date <= contract.today and contract.end_date <= contract.today:
                    contract.contract_state = 'منتهي'
                else:
                    contract.contract_state = 'جديد'   

    def _count_days(self):
        for contract in self:
            if contract.start_date and contract.end_date:
                date_start = fields.Date.from_string(contract.start_date)
                date_end = fields.Date.from_string(contract.end_date)
                today = fields.Date.from_string(date.today())
                contract.count_days = (date_end - date_start).days
            else:
                contract.count_days = False
                

    price_day = fields.Float(string='سعر المتر اليومي بالريال', compute='_price_day', digits=(12,2))
    
    @api.depends('meter_price', 'count_days')
    def _price_day(self):
        for contract in self:
            if contract.count_days and contract.meter_price:
                contract.price_day = (contract.meter_price or 0.0) / (contract.count_days or 1)
            else:
                contract.price_day = False
                
    paid_amount = fields.Float(string='مجموع المبالغ المدفوعة', compute='_paid_amount', digits=(12,2))
    amount_left = fields.Float(string='المبالغ المتبقية', compute='_amount_left', digits=(12,2))
    days_left = fields.Float(string='الأيام المتبقية على إنتهاء العقد', compute='_days_left', digits=(12,2))
    taxs = fields.Float(string='مبلغ الضريبة المضافة', compute='_paid_taxs', digits=(12,2))
    amount_taxed = fields.Float(string='المبلغ الإجمالي', compute='_amount_taxed', digits=(12,2))
    
    def _paid_amount(self):
        for contract in self:
            paid_amount = 0
            for payment in contract.payment_ids:
                paid_amount += payment.paid_amount
            contract.paid_amount = paid_amount
            
    def _paid_taxs(self):
        for contract in self:
            taxs = 0
            for payment in contract.payment_ids:
                taxs += payment.taxs
            contract.taxs = taxs
            
    def _amount_taxed(self):
        for contract in self:
            contract.amount_taxed = contract.taxs + contract.paid_amount

    def _amount_left(self):
        for contract in self:
            if contract.rent_amount:
                contract.amount_left = contract.rent_amount - (contract.paid_amount or 0)
            else:
                contract.amount_left = 0
                
    def _days_left(self):
        for contract in self:
            days_left = 0
            if contract.end_date and contract.end_date > date.today():
                days_left = (contract.end_date - date.today()).days
                contract.days_left = days_left
            else:
                contract.days_left = False
    
class payment(models.Model):
    _name = 'payment.payment'
    _description = 'payment'
    _inherit = []
    _order = 'id'
            
    name = fields.Char("الدفعات", required=True)
    company_id = fields.Many2one(related='user_id.company_id')
    user_id = fields.Many2one(related='contract_id.user_id')
    payment_amount = fields.Float(string='مبلغ الدفعة', store=True, required=True, digits=(12,2))
    payment_date = fields.Date(string='تاريخ الدفعة', index=True, required=True)
    company_currency = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id', readonly=True)
    contract_id = fields.Many2one('contract.contract', string='عقد الإيجار', auto_join=True)
    partner_id = fields.Many2one('res.partner', related='contract_id.partner_id', string='العميل', auto_join=True)
    partner_employee = fields.Many2one(related='contract_id.partner_employee')
    payment_type = fields.Selection([
        ('تم السداد', 'استحقت الدفعة وسدد'),
        ('لم يتم السداد', 'استحقت الدفعة ولم يسدد'),
        ('لم يحن موعد استحقاق الدفعة', 'لم يحن موعد استحقاق الدفعة')
        ], string='حالة السداد', store=True, copy=False, readonly=False, required=True, compute='_is_it_there')
    note = fields.Text(string='ملاحظات')
                        
    @api.depends('payment_date')
    def _is_it_there(self):
        for payment in self:
            today = date.today()
            if payment.payment_date:
                if payment.payment_date >= today:
                    payment.payment_type = 'لم يحن موعد استحقاق الدفعة'
    
    payment_full = fields.Selection([
        ('سداد كامل', 'سداد كامل'),
        ('سداد جزئي', 'سداد جزئي'),
        ], string='نوع السداد', store=True)
    partial_payment = fields.Float(string='المبلغ الجزئي المدفوع', digits=(12,2))
    
    tax_paid = fields.Selection([
        ('لا', 'لا'),
        ('نعم كاملة', 'نعم كاملة'),
        ('نعم بشكل جزئي', 'نعم بشكل جزئي'),
        ], string='هل تم سداد قيمة الضريبة المضافة؟', store=True)
    partial_tax = fields.Float(string='مبلغ الضريبة الجزئي المدفوع')
    
    taxs = fields.Float(string='مبلغ الضريبة المضافة', compute='_paid_taxs', digits=(12,2))
    
    def _paid_taxs(self):
        for payment in self:
            if payment.tax_paid:
                if payment.tax_paid == 'لا':
                    paid_amount = 0
                elif payment.tax_paid == 'نعم كاملة':
                    paid_amount = (payment.payment_amount * 0.15)
                elif payment.tax_paid == 'نعم بشكل جزئي':
                    paid_amount = payment.partial_tax
                payment.taxs = paid_amount
            else:
                payment.taxs = False
    
    paid_amount = fields.Float(string='المبلغ المدفوع', compute='_paid_amount')
    
    def _paid_amount(self):
        for payment in self:
            if payment.payment_type == 'تم السداد':
                if payment.payment_full == 'سداد كامل': 
                    paid_amount = payment.payment_amount
                elif payment.payment_full == 'سداد جزئي':
                    paid_amount = payment.partial_payment
                else:
                    paid_amount = False
                payment.paid_amount = paid_amount
            else:
                payment.paid_amount = False
                
    def _payment_today(self):
        for payment in self.env['payment.payment'].search([('payment_type', 'not in', ('تم السداد','لم يتم السداد'))]):
            today = date.today()
            if payment.payment_date:
                if payment.payment_date == today:
                    base_url = payment.company_id.website
                    url = base_url + '/web#id=%d&model=payment.payment&view_type=form' % (payment.id)
                    body_html = ("تشير السجلات بأن موعد سداد " + payment.name + " لعقد " + payment.contract_id.name + " في وحدة " 
                                 + payment.contract_id.unit_id.name + " التابعة لمبنى "  + payment.contract_id.unit_id.building_id.name 
                                 + " تحت إدارة " + payment.contract_id.unit_id.building_id.estate_id.partner_id.name 
                                 + " قد استحق بتاريخ " + str(payment.payment_date)
                                 + " نأمل منكم متابعة السداد وتحديث الحالة في النظام. وشكرا"
                                 + '<div>.</div>' 
                                 + '<a href="%s"style="padding: 8px 16px 8px 16px; border-radius: 3px; background-color:#875A7B; text-align:center; text-decoration:none; color: #FFFFFF;">للإطلاع</a>' % url)
                    subject = ("استحقاق موعد سداد " + payment.name)
                    vals = {
                        'subject': subject,
                        'body_html': body_html,
                        'author_id': payment.user_id.partner_id.id,
                        'email_from': payment.user_id.company_id.partner_id.email_formatted or payment.user.email_formatted,
                        'email_to': payment.user_id.partner_id.email,
                        'auto_delete': True,
                        'state': 'outgoing'
                    }
                    self.env['mail.mail'].sudo().create(vals).send()
