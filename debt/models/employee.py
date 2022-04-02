# Copyright to The City Law Firm
from odoo import models, fields, api



class employeesinfo(models.Model):
    _inherit = 'hr.employee'

    violation_ids = fields.One2many("violations.violations", 'employee_id', string="المخالفات", groups="hr.group_hr_user", readonly=True)
    debt_ids = fields.One2many("debt.debt", 'employee_id', string="المديونيات", groups="hr.group_hr_user", readonly=True)