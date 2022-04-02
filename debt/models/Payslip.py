# Copyright to The City Law Firm
from odoo import models, fields, api, _
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning


class Payslips_inherit(models.Model):
    _inherit = 'hr.payslip'

    normal_wage = fields.Float(compute='_compute_paysli_normal_wage', store=True)    
    violations_amount = fields.Float(string='مجموع مبالغ المخالفات', compute="_compute_total")
    absence_amount = fields.Float(compute="_compute_total")
    bonus = fields.Float(string='مكافأة الشهر')
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('verify', 'في الانتظار'),
        ('confirm', 'تأكيد'),
        ('approved', 'موافق عليها'),
        ('done', 'منتهية'),
        ('paid', 'مدفوعة'),
        ('cancel', 'مرفوضة')],
        string='الحالة', index=True, readonly=True, copy=False)

    
    url = fields.Char(compute='get_url')
    
    def get_url(self):
        for payslip in self:
            base_url = payslip.company_id.website
            payslip.url = base_url + '/web#id=' + str(payslip.id) + '&model=hr.payslip&view_type=form'

    
    def action_payslip_done(self):
        for payslip in self:
            if payslip.state != 'approved':
                raise UserError(('يجب أن يتم الموافقة على الراتب من قبل المدير العام'))
        return super(Payslips_inherit, self).action_payslip_done()

    
    def action_payslip_approve(self):
        for payslip in self:
            payslip.write({'state': 'approved'})

    def action_payslip_confirm(self):
        for payslip in self:
            payslip.write({'state': 'confirm'})

    
    @api.depends('contract_id')
    def _compute_paysli_normal_wage(self):
        for payslip in self:
            contract = payslip.contract_id
            payslip.normal_wage = contract.wage + contract.l10n_sa_housing_allowance + contract.l10n_sa_transportation_allowance + contract.l10n_sa_other_allowances + contract.basic_remain

    def _compute_total(self):
        for payslip in self:
            violations_amount = 0
            amount = 0
            number_of_days = 0
            contract = self.contract_id
            absence_amount = False
            paid_amount = 0
            total_amount = 0
            for line in payslip.worked_days_line_ids:
                total_amount += line.amount
                
            number_of_days = (payslip.date_to - payslip.date_from).days + 1
            paid_amount = total_amount
            wage = contract.wage + contract.l10n_sa_housing_allowance + contract.l10n_sa_transportation_allowance + contract.l10n_sa_other_allowances + contract.basic_remain
            per_day = (wage) / (number_of_days or 1)

            amount_of_higher_count = 0
            violation_type_obj=self.env['violations.type']
            all_violation_type=violation_type_obj.search([])
            for violation in all_violation_type:
                violations_id = self.env['violations.violations'].search([('employee_id', '=', self.employee_id.id),
                                                                             ('caliming_date', '<=', self.date_to),
                                                                             ('caliming_date', '>=', self.date_from),
                                                                             ('state', '=', 'approved'),('violation','=',violation.id)])
                if len(violations_id)>1:
                    max_count=0
                    final_violation_browse_id=False
                    for filter_violation in violations_id:
                        if filter_violation.count > max_count:
                            max_count=filter_violation.count
                            final_violation_browse_id=filter_violation
                    if final_violation_browse_id!=False:
                        amount_of_higher_count += final_violation_browse_id.amount
                else:
                    amount_of_higher_count += violations_id.amount
                    final_violation_browse_id=violations_id

            violations_amount += amount_of_higher_count
                        
            amount = violations_amount * per_day   
            max_violation = per_day * 5
            if amount > max_violation:
                violations_amount = max_violation
            else:
                violations_amount = violations_amount * per_day
            payslip.violations_amount = violations_amount
            
            if paid_amount < wage:
                absence_amount = paid_amount
            payslip.absence_amount = absence_amount

            
    debts_amount = fields.Float(string='مجموع مبالغ المديونيات', compute="_compute_total_debt")
    
    def _compute_total_debt(self):
        for payslip in self:
            debts_id = self.env['debt.debt'].search([('employee_id', '=', self.employee_id.id),
                                                                     ('caliming_date', '<=', self.date_to),
                                                                     ('caliming_date', '>=', self.date_from),
                                                                     ('state', '=', 'approved')])
            debts_amount = 0
            for debt in debts_id:
                debts_amount += debt.debt_amount
            payslip.debts_amount = (debts_amount)
            
            
    def _compute_basic_net(self):
        for payslip in self:
            payslip.basic_wage = payslip._get_salary_line_total('أساسي')
            payslip.net_wage = payslip._get_salary_line_total('صافي')
            

    
    
    
    
    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
        """
        :returns: a list of dict containing the worked days values that should be applied for the given payslip
        """
        res = []
        # fill only if the contract as a working schedule linked
        self.ensure_one()
        contract = self.contract_id
        if contract.resource_calendar_id:
            res = self._get_worked_day_lines_values(domain=domain)
            if not check_out_of_contract:
                return res

            # If the contract doesn't cover the whole month, create
            # worked_days lines to adapt the wage accordingly
            out_days, out_hours = 0, 0
            reference_calendar = self._get_out_of_contract_calendar()
            if self.date_from < contract.date_start:
                start = fields.Datetime.to_datetime(self.date_from)
                stop = fields.Datetime.to_datetime(contract.date_start) + relativedelta(days=-1, hour=23, minute=59)
                out_time = (stop - start) + relativedelta(days=1)
                out_days = out_time.days
                out_hours = out_days * self.contract_id.hours_per_day
            if contract.date_end and contract.date_end < self.date_to:
                start = fields.Datetime.to_datetime(contract.date_end) + relativedelta(days=1)
                stop = fields.Datetime.to_datetime(self.date_to) + relativedelta(hour=23, minute=59)
                out_time = (stop - start) + relativedelta(days=1)
                out_days = out_time.days
                out_hours = out_days * self.contract_id.hours_per_day

            if out_days or out_hours:
                work_entry_type = self.env.ref('hr_payroll.hr_work_entry_type_out_of_contract')
                res.append({
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type.id,
                    'number_of_days': out_days,
                    'number_of_hours': out_hours,
                })
        return res


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    bonus = fields.Float(string='مكافأة الشهر')

    @api.depends('is_paid', 'number_of_hours', 'payslip_id', 'payslip_id.normal_wage', 'number_of_days')
    def _compute_amount(self):
        for worked_days in self.filtered(lambda wd: not wd.payslip_id.edited):
            if not worked_days.contract_id:
                worked_days.amount = 0
                continue
            if worked_days.payslip_id.wage_type == "hourly":
                worked_days.amount = - (worked_days.payslip_id.contract_id.hourly_wage * worked_days.number_of_hours if not worked_days.is_paid else 0)
            else:
                worked_days.amount = - ((worked_days.payslip_id.normal_wage / ((worked_days.payslip_id.date_to - worked_days.payslip_id.date_from).days + 1)  or 1 ) *  worked_days.number_of_days if not worked_days.is_paid else 0)
