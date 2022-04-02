# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    
    def delete_payslip(self):
        self.write({'state' : 'cancel'})

    
class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    
    def delete_payslip_run(self):
        self.write({'state' : 'draft'})
