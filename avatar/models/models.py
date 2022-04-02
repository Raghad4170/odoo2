# Copyright to The City Law Firm
from odoo import models, fields


class Contact(models.AbstractModel):
    _inherit = 'ir.qweb.field.contact'

    
    
class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    attendance_state = fields.Selection(groups="base.group_user,base.group_portal")
    hours_today = fields.Float(groups="base.group_user,base.group_portal")
    last_attendance_id = fields.Many2one(groups="base.group_user,base.group_portal")
    last_check_in = fields.Datetime(groups="base.group_user,base.group_portal")
    last_check_out = fields.Datetime(groups="base.group_user,base.group_portal")
    
    holidays_allocations = fields.Many2many('hr.leave.allocation', groups="base.group_user,base.group_portal")
    
class HrEmployee(models.Model):
    _inherit = "hr.employee"

    attendance_state = fields.Selection(groups="base.group_user,base.group_portal")
    hours_today = fields.Float(groups="base.group_user,base.group_portal")
    last_attendance_id = fields.Many2one(groups="base.group_user,base.group_portal")
    last_check_in = fields.Datetime(groups="base.group_user,base.group_portal")
    last_check_out = fields.Datetime(groups="base.group_user,base.group_portal")

    
    holidays_allocations = fields.Many2many('hr.leave.allocation', groups="base.group_user,base.group_portal")
        
    def _compute_all_slip_ids(self):
        for employee in self:
            data = self.env['hr.leave.allocation'].search([
                ('employee_id', '=', employee.id),
                ('holiday_status_id.active', '=', True),
                ('state', '=', 'validate')])
            employee.holidays_allocations = data
    
class allocation(models.Model):
    _inherit = "hr.leave.allocation"
    
    

    leave_remaining_employee = fields.Char(compute='_compute_leave_remaining_employee')
    
    def _compute_leave_remaining_employee(self):
        for allocation in self:
            total=(allocation.max_leaves - allocation.leaves_taken)
            allocation.leave_remaining_employee = total