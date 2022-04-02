# Copyright to Mutn
from odoo import models, fields, api
from datetime import datetime, time
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning


class employeedebt(models.Model):
    _name = 'employee.debts'
    _description = 'employee debts'
    
    name = fields.Char("المديونية")
    employee_id = fields.Many2one('hr.employee', string='الموظف', index=True)
    company_id = fields.Many2one(related='employee_id.company_id')
    debt_ids = fields.One2many('debt.debt', 'employee_debts', string='المديونيات')
    
    debts_confirm = fields.Integer(string='المعلقة', compute="_compute_total")
                
    def _compute_total(self):
        debt_id = self.env['debt.debt'].read_group([('employee_debts', '=', self.ids), ('state', '=', 'confirm')], ['employee_debts'], ['employee_debts'])
        result = dict((data['employee_debts'][0], data['employee_debts_count']) for data in debt_id)
        for debts in self:
            debts.debts_confirm = result.get(debts.id, 0)
            
    debts_refuse = fields.Integer(string='المعفية', compute="_compute_refuse")
                
    def _compute_refuse(self):
        debt_id = self.env['debt.debt'].read_group([('employee_debts', '=', self.ids), ('state', '=', 'refuse')], ['employee_debts'], ['employee_debts'])
        result = dict((data['employee_debts'][0], data['employee_debts_count']) for data in debt_id)
        for debts in self:
            debts.debts_refuse = result.get(debts.id, 0)
            
    debts_approved = fields.Integer(string='المؤكدة', compute="_compute_approved")
                
    def _compute_approved(self):
        debt_id = self.env['debt.debt'].read_group([('employee_debts', '=', self.ids), ('state', '=', 'approved')], ['employee_debts'], ['employee_debts'])
        result = dict((data['employee_debts'][0], data['employee_debts_count']) for data in debt_id)
        for debts in self:
            debts.debts_approved = result.get(debts.id, 0)

            
class Debt(models.Model):
    _name = 'debt.debt'
    _description = 'debt'
    _order = 'state'
    
    name = fields.Char("المديونية")
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('confirm', 'للموافقة'),
        ('refuse', 'إعفاء'),
        ('approved', 'مؤكد')
        ], string='الحالة', readonly=True, copy=False, default='draft')
    employee_debts = fields.Many2one("employee.debts", string="المديونيات", required=True)
    employee_id = fields.Many2one('hr.employee', string='الموظف', related='employee_debts.employee_id', index=True)
    caliming_date = fields.Date(string='تاريخ الاستحقاق', index=True)
    debt_amount = fields.Monetary(string='المبلغ', store=True, currency_field='company_currency')
    company_currency = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    summary = fields.Text(string='ملخص المديونية')
    
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_confirm(self):
        self.write({'state': 'confirm'})
        return True

    def action_refuse(self):
        self.write({'state': 'refuse'})
        return True

    def action_approve(self):
        if self.caliming_date:
            self.write({'state': 'approved'})
        else:
                raise UserError(('لا يمكنك تأكيد مديونية بدون تاريخ إستحقاق لها!'))
        return True
    
    def unlink(self):
        for debt in self:
            if debt.state == 'approved':
                raise UserError(('لا يمكنك حذف مديونية تم تأكيدها!'))
            elif debt.state == 'refuse':
                raise UserError(('لا يمكنك حذف مديونية معفي عنها!'))
        result = super(Debt, self).unlink()
        return result