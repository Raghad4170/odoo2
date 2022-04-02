# Copyright to The City Law Firm
from odoo import models, fields, api

            
class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    housing_allowance = fields.Monetary(string='بدل السكن', tracking=True, help="بدل السكن")
    transporting_allowance = fields.Monetary(string="بدل المواصلات", help="بدل المواصلات")
    other_allowance = fields.Monetary(string="بدلات أخرى", help="بدلات أخرى")
    basic_remain = fields.Monetary(string="المتبقي من الراتب", help="المتبقي من الراتب لا يدخل في التأمينات")
    resource_calendar_id = fields.Many2one(related='employee_id.resource_calendar_id')
    hours_per_day = fields.Float(related='resource_calendar_id.hours_per_day')