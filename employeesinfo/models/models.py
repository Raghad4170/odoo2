# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    report = fields.Binary('إرفاق تقرير', store=True)

class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    leaves_got_taken = fields.Float(string='الإجازات', compute='_compute_leaves_got_taken')

    def _compute_leaves_got_taken(self):
        for allocation in self:
            leaves_taken = 0.0
            requests = self.env['hr.leave'].search([
                ('employee_id', '=', allocation.employee_id.id),
                ('state', 'in', ['confirm', 'validate1', 'validate']),
                ('holiday_status_id', '=', allocation.holiday_status_id.id)])
            for request in requests:
                leaves_taken += (request.number_of_hours_display if request.leave_type_request_unit == 'hour'
                                 else request.number_of_days)
            allocation.leaves_got_taken = leaves_taken

class ResumeLine(models.Model):
    _inherit = 'hr.resume.line'

    certificate = fields.Binary('ملف الشهادة', store=True)


class account_move(models.Model):
    _inherit = 'account.move'

    employee_id = fields.Many2one(related='invoice_user_id.employee_id')

class emp_exp(models.Model):
    _name = 'emp.exp'
    _description = 'المصروفات'

    name = fields.Char("الاسم")
    price = fields.Float("المبلغ")
    emp_exp_id = fields.Many2one('hr.employee')

class emp_rev(models.Model):
    _name = 'emp.rev'
    _description = 'الإيرادات'

    name = fields.Char("الاسم")
    price = fields.Float("المبلغ")
    emp_exp_id = fields.Many2one('hr.employee')


class employeesinfopublic(models.Model):
    _inherit = 'hr.employee.public'
    
    permit_no = fields.Char(related='employee_id.permit_no')

class employeesinfo(models.Model):
    _inherit = 'hr.employee'
    
    @api.onchange('is_company_partner') 
    def _get_is_company_partner(self):
        for record in self:
            create = False
            employee = record.user_id.employee_id.id
            partner = self.env['partners.reports'].sudo().search([('employee_id', '=', record.user_id.employee_id.id)], limit=1)
            if partner.id == record.id:
                if record.is_company_partner != True:
                    partner.unlink()                    
            else:
                if record.is_company_partner == True:
                    create = True
            if create == True:
                vals = {
                    'employee_id': employee,
                }
                self.env['partners.reports'].sudo().create(vals)
    
    permit_no = fields.Char(groups="base.group_user")

    is_company_partner = fields.Boolean("شريك", groups="hr.group_hr_user", store=True)

    all_exp = fields.Float(compute='_compute_all_exp', groups="hr.group_hr_user")

    def _compute_all_exp(self):
        for employee in self:
            exp_amount = 0
            payslips_amount = 0
            if employee.payslips_amount:
                payslips_amount = employee.payslips_amount
            if employee.exp_amount:
                exp_amount = employee.exp_amount
            employee.all_exp = payslips_amount + exp_amount


    total_exp_move = fields.Float(compute='_compute_total_exp_move', groups="hr.group_hr_user")

    def _compute_total_exp_move(self):
        for employee in self:
            move_amount = 0
            all_exp = 0
            if employee.all_exp:
                all_exp = employee.all_exp
            if employee.move_amount:
                move_amount = employee.move_amount
            employee.total_exp_move = move_amount - all_exp
            
            
    payslips_users = fields.Many2many('res.users', string='رواتب التابعين', domain="[('share', '=', False)]", groups="hr.group_hr_user")

    all_slips = fields.Many2many('hr.payslip', string='الرواتب', compute='_compute_all_slip_ids', groups="hr.group_hr_user")
    
    def _compute_all_slip_ids(self):
        for employee in self:
            employee_slips = []
            slips = employee.slip_ids
            all_slip = employee.slip_ids
            if employee.payslips_users:
                for user in employee.payslips_users:
                    slips += user.employee_id.slip_ids
            all_slip = slips
            employee_slips = employee.slip_ids
            employee.all_slips = employee_slips + all_slip


    payslips_amount = fields.Float(compute='_compute_payslips_amount', groups="hr.group_hr_user")

    def _compute_payslips_amount(self):
        for employee in self:
            amount = 0
            for slip in employee.all_slips:
                amount += slip.net_wage
            employee.payslips_amount = amount


    exp_amount = fields.Float(compute='_compute_exp_amount', groups="hr.group_hr_user")

    def _compute_exp_amount(self):
        for employee in self:
            amount = 0
            for exp in employee.emp_exp:
                amount += exp.price
            employee.exp_amount = amount

    emp_exp = fields.One2many('emp.exp','emp_exp_id', 'المصاريف', groups="hr.group_hr_user")

    rev_amount = fields.Float(compute='_compute_emp_rev', groups="hr.group_hr_user")

    def _compute_emp_rev(self):
        for employee in self:
            amount = 0
            for rev in employee.emp_rev:
                amount += rev.price
            employee.rev_amount = amount

    emp_rev = fields.One2many('emp.rev','emp_exp_id', 'الإيرادات', groups="hr.group_hr_user")


    move_amount = fields.Float(compute='_compute_move_amount', groups="hr.group_hr_user")

    def _compute_move_amount(self):
        for employee in self:
            amount = 0
            for move in employee.move_id:
                amount += move.amount_untaxed_signed
            employee.move_amount = amount


    move_id = fields.One2many('account.move','employee_id', 'إيرادات العملاء', groups="hr.group_hr_user")

    building_no = fields.Char(string='رقم المبنى', groups="hr.group_hr_user")
    street = fields.Char(string='اسم الشارع', groups="hr.group_hr_user")
    neighborhood = fields.Char(string='اسم الحي', groups="hr.group_hr_user")
    city = fields.Char(string='اسم المدينة', groups="hr.group_hr_user")
    box_no = fields.Char(string='الرمز البريدي', groups="hr.group_hr_user")
    ad_no = fields.Char(string='الرقم الاضافي', groups="hr.group_hr_user")
    first_name = fields.Char(string='الاسم الأول', groups="hr.group_hr_user")
    second_name = fields.Char(string='اسم الأب', groups="hr.group_hr_user")
    third_name = fields.Char(string='اسم الجد', groups="hr.group_hr_user")
    last_name = fields.Char(string='اللقب', groups="hr.group_hr_user")

    Kinship = fields.Selection([
        ('أم', 'أم'),
        ('أب', 'أب'),
        ('أخ', 'أخ'),
        ('أخت', 'أخت'),
        ('زوجة', 'زوجة'),
        ('زوج', 'زوج'),
        ('أبن', 'أبن'),
        ('أبنة', 'أبنة')
    ], string='جهة القرابة', groups="hr.group_hr_user", readonly=False)

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], groups="hr.group_hr_user", tracking=True)
    employees_affiliate = fields.One2many(
        'affiliates', "employee_id", string='التابعين', groups="hr.group_hr_user")

    tasks = fields.Char(compute='_compute_tasks', string='Tasks', groups="hr.group_hr_user")
    tasks_count = fields.Integer(compute='_compute_tasks', string='Tasks count', groups="hr.group_hr_user")

    def _compute_tasks(self):
        for employee in self:
            user = employee.user_id
            if user:
                tasks = self.env['project.task'].sudo().search([('user_ids','=',user.id)])
                employee.tasks = "Tasks: " + str(len(tasks))
                employee.tasks_count = str(len(tasks))
            else:
                employee.tasks_count = 0

    def display_employee_tasks(self):
        if self.user_id:
            context="{'group_by':'state_id'}"
            template_id = self.env.ref('project.view_task_kanban').id
            search_id = self.env.ref('project.view_task_search_form').id
            return {
                'name': 'المهام',
                'view_type': 'kanban',
                'view_mode': 'kanban,form',
                'res_model': 'project.task',
                'type': 'ir.actions.act_window',
                'view_id': template_id,
                'views': [(self.env.ref('project.view_task_kanban').id, 'kanban'),
                          (self.env.ref('project.view_task_form2').id, 'form')],
                'search_view_id': search_id,
                'domain': [('user_ids','=',self.user_id.id)],
                'context': context
             }


    project = fields.Char(compute='_compute_project', string='Projects', groups="hr.group_hr_user")
    project_count = fields.Integer(compute='_compute_project', string='Projects count', groups="hr.group_hr_user")

    def _compute_project(self):
        for employee in self:
            user = employee.user_id
            if user:
                project = self.env['project.project'].sudo().search([('user_id','=',user.id)])
                employee.project = "project: " + str(len(project))
                employee.project_count = str(len(project))
            else:
                employee.project_count = 0

    def display_employee_project(self):
        if self.user_id:
            template_id = self.env.ref('project.view_project').id
            search_id = self.env.ref('project.view_project_project_filter').id
            context="{}"
            return {
                'name': 'المشاريع',
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'project.project',
                'type': 'ir.actions.act_window',
                'view_id': template_id,
                'views': [(self.env.ref('project.view_project').id, 'list'),
                          (self.env.ref('project.edit_project').id, 'form')],
                'search_view_id': search_id,
                'domain': [('user_id','=',self.user_id.id)],
                'context': context
             }

class User(models.Model):
    _inherit = ['res.users']
    
    
#     payslips_amount = fields.Float(compute='_get_payslips_amount', store=True)
    
#     @api.depends('employee_id','employee_id.payslips_amount','employee_id.all_slips') 
#     def _get_payslips_amount(self):
#         for user in self:
#             amount = 0
#             if user.employee_id.payslips_amount:
#                 amount = user.employee_id.payslips_amount
#             user.payslips_amount = amount
            
    building_no = fields.Char(string='رقم المبنى', related='employee_id.building_no', readonly=False)
    street = fields.Char(string='اسم الشارع', related='employee_id.street', readonly=False)
    neighborhood = fields.Char(string='اسم الحي', related='employee_id.neighborhood', readonly=False)
    city = fields.Char(string='اسم المدينة', related='employee_id.city', readonly=False)
    box_no = fields.Char(string='الرمز البريدي', related='employee_id.box_no', readonly=False)
    ad_no = fields.Char(string='الرقم الاضافي', related='employee_id.ad_no', readonly=False)
    first_name = fields.Char(string='الاسم الأول', related='employee_id.first_name', readonly=False)
    second_name = fields.Char(string='اسم الأب', related='employee_id.second_name', readonly=False)
    third_name = fields.Char(string='اسم الجد', related='employee_id.third_name', readonly=False)
    last_name = fields.Char(string='اللقب', related='employee_id.last_name', readonly=False)
    Kinship = fields.Selection(
        related='employee_id.Kinship', readonly=False, related_sudo=False)
    employees_affiliate = fields.One2many(
        related='employee_id.employees_affiliate', readonly=False, related_sudo=False)

    @api.depends('employee_ids')
    def _compute_employee_count(self):
        for user in self.with_context(active_test=False):
            user.employee_count = len(user.employee_ids)

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['employee_parent_id','employees_affiliate','building_no','payslips_amount','street','neighborhood','city','box_no','ad_no','first_name','second_name','third_name','last_name','Kinship']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ['employees_affiliate','building_no','street','neighborhood','city','box_no','ad_no','first_name','second_name','third_name','last_name','Kinship']

class employees_affiliates(models.Model):
    _name = 'affiliates'
    _description = 'التابعين'

    employee_id = fields.Many2one('hr.employee', string="Employee", ondelete='cascade')
    name = fields.Char(string='الاسم', index=True, required=True)
    Kinship = fields.Selection([
        ('زوجة', 'زوجة'),
        ('زوج', 'زوج'),
        ('أبن', 'أبن'),
        ('أبنة', 'أبنة')
    ], string='جهة القرابة', readonly=False, required=True)
    date_of_barth = fields.Date(string='تاريخ الميلاد', required=True)
    national_id = fields.Char(string="رقم الهوية", required=True)