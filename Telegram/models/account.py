# -*- coding: utf-8 -*-
from odoo import models, api, _, fields
from odoo.tools.misc import formatLang
import requests
from urllib.parse import quote_plus

class bills_telegram(models.Model):
    _inherit = 'bills.management'

    def action_accountant_approve(self):
        for bill in self:
            if bill.company_id.telegram_token:
                users = self.env['res.users'].sudo().search([])
                for user in users:
                    if user.has_group('parentid.bills_officer'):
                        employee = bill.employee_id.name
                        name = bill.name
                        expense_amount = formatLang(self.env, bill.expense_amount)
                        url = ("%3Ca+href%3D%27{}".format(quote_plus(bill.url)))
                        message = 'تم مراجعة صحة فاتورة ' + name + ' المرفوعة من قبل الموظف ' + employee + ' بالمبلغ: ' + expense_amount + ' من قبل المحاسبة، نأمل منكم مراجعتها والتوصية بإعتمادها.' 
                        quote_message =  url + '%27%3E' + ("{}".format(quote_plus(message))) + '%3C%2Fa%3E'
                        chat_id = user.chat_id
                        token = bill.company_id.telegram_token
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + quote_message
                        response = requests.post(send_text)
        return super(bills_telegram, self).action_accountant_approve()

    def action_hr_approve(self):
        for bill in self:
            if bill.company_id.telegram_token:
                users = self.env['res.users'].sudo().search([])
                for user in users:
                    if user.has_group('parentid.director'):
                        employee = bill.employee_id.name
                        name = bill.name
                        expense_amount = formatLang(self.env, bill.expense_amount)
                        url = ("%3Ca+href%3D%27{}".format(quote_plus(bill.url)))
                        message = 'تم التوصية بإعتماد فاتورة ' + name + ' المرفوعة من قبل الموظف ' + employee + ' بالمبلغ: ' + expense_amount + ' نأمل منكم الموافقة عليها.' 
                        quote_message =  url + '%27%3E' + ("{}".format(quote_plus(message))) + '%3C%2Fa%3E'
                        chat_id = user.chat_id
                        token = bill.company_id.telegram_token
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + quote_message
                        response = requests.post(send_text)
        return super(bills_telegram, self).action_hr_approve()

class Payslips_telegram(models.Model):
    _inherit = 'hr.payslip'
    
    
    def action_payslip_confirm(self):
        for payslip in self:
            if payslip.company_id.telegram_token:
                users = self.env['res.users'].sudo().search([])
                for user in users:
                    if user.has_group('parentid.director'):
                        name = payslip.employee_id.name
                        net_wage = formatLang(self.env, payslip.net_wage)
                        url = ("%3Ca+href%3D%27{}".format(quote_plus(payslip.url)))
                        message = 'تم إصدار راتب ' + name + ' بالمبلغ: ' + net_wage 
                        quote_message =  url + '%27%3E' + ("{}".format(quote_plus(message))) + '%3C%2Fa%3E'
                        chat_id = user.chat_id
                        token = payslip.company_id.telegram_token
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + quote_message
                        response = requests.post(send_text)
        return super(Payslips_telegram, self).action_payslip_confirm()



class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    late_unpaid_inv = fields.Float(compute='_late_unpaid_inv_get')
    partial_unpaid_inv = fields.Float(compute='_late_unpaid_inv_get')
    draft_unpaid_inv = fields.Float(compute='_late_unpaid_inv_get')
    
    def _late_unpaid_inv_get(self):
        for partner in self:
            des_inv = 0
            part_inv = 0
            dar_inv = 0
            unpaid_inv = self.env['account.move'].sudo().search([('payment_state', '=', 'not_paid'),
                                                                 ('state', '=', 'posted'),
                                                                 ('journal_id.type', '=', 'sale'),
                                                                 ('partner_id', '=', partner.id)])

            partial_inv = self.env['account.move'].sudo().search([('payment_state', '=', 'partial'),
                                                                 ('state', '=', 'posted'),
                                                                 ('journal_id.type', '=', 'sale'),
                                                                 ('partner_id', '=', partner.id)])
            
            draft_inv = self.env['account.move'].sudo().search([('state', '=', 'draft'),
                                                                 ('journal_id.type', '=', 'sale'),
                                                                 ('partner_id', '=', partner.id)])
            for unpaid in unpaid_inv:
                des_inv += unpaid.amount_total_signed
            for partial in partial_inv:
                part_inv += partial.amount_residual
            for draft in draft_inv:
                dar_inv += draft.amount_total_signed
            partner.late_unpaid_inv = des_inv
            partner.partial_unpaid_inv = part_inv
            partner.draft_unpaid_inv = dar_inv

                             
class account_journal(models.Model):
    _inherit = "account.journal"
            
    def update_data_telegram(self):
        companies = self.env['res.company'].sudo().search([])
        for company in companies:
            if company.bank_telegram and company.telegram_token:
                bank_info = ''
                total = ''
                des_all = ''
                unpaid_invoices  = ''
                partial_invoices = ''
                draft_invoices = ''
                unpaid_all = ''
                partial_all = ''
                drafts_all = ''
                all_tot = ''
                total_bank = 0
                des_inv = 0
                late_unpaid_inv = 0
                partial_unpaid_inv = 0
                draft_unpaid_inv = 0
                totall_all = 0
                banks = self.env['account.journal'].sudo().search([('type','=','bank'),('company_id', '=', company.id)])
                for bank in banks:
                    currency = bank.currency_id or bank.company_id.currency_id
                    name = bank.name
                    bank_account_balance, nb_lines_bank_account_balance = bank._get_journal_bank_account_balance(
                        domain=[('move_id.state', '=', 'posted')])
                    outstanding_pay_account_balance, nb_lines_outstanding_pay_account_balance = bank._get_journal_outstanding_payments_account_balance(
                        domain=[('move_id.state', '=', 'posted')])
                    total_account_balance = formatLang(self.env, bank_account_balance + outstanding_pay_account_balance)
                    bank_info += name + ': ' + str(total_account_balance) + '\n'

                banks_tot = self.env['account.journal'].sudo().search([('type','=','bank'),('name','not ilike','ضرائب'),('company_id', '=', company.id)])
                for bank_tot in banks_tot:
                    bank_account_balance, nb_lines_bank_account_balance = bank_tot._get_journal_bank_account_balance(
                        domain=[('move_id.state', '=', 'posted')])
                    outstanding_pay_account_balance, nb_lines_outstanding_pay_account_balance = bank_tot._get_journal_outstanding_payments_account_balance(
                        domain=[('move_id.state', '=', 'posted')])
                    total_account_balance = bank_account_balance + outstanding_pay_account_balance
                    total_bank += total_account_balance
                    total = formatLang(self.env, total_bank)

                get_all_customers_id = self.env['res.partner'].sudo().search([('company_id', '=', company.id)])

                for customer in get_all_customers_id:
                    name = customer.name

                    late_unpaid_inv = customer.late_unpaid_inv
                    if late_unpaid_inv > 0:
                        unpaid_amount = formatLang(self.env, late_unpaid_inv)
                        unpaid_invoices += name + ': ' + str(unpaid_amount) + '\n'
                        unpaid_all = 'المبالغ المستحقة: ' + '\n' + unpaid_invoices

                    partial_unpaid_inv = customer.partial_unpaid_inv
                    if partial_unpaid_inv > 0:
                        partial_amount = formatLang(self.env, partial_unpaid_inv)
                        partial_invoices +=  name + ': ' + str(partial_amount) + '\n'
                        partial_all = 'المبالغ المدفوعة جزئيا: ' + '\n' + partial_invoices

                    draft_unpaid_inv = customer.draft_unpaid_inv
                    if draft_unpaid_inv > 0:
                        draft_amount = formatLang(self.env, draft_unpaid_inv)
                        draft_invoices +=  name + ': ' + str(draft_amount) + '\n'
                        drafts_all = 'المبالغ الغير مستحقة:' + '\n' + draft_invoices

                    des_inv += late_unpaid_inv + partial_unpaid_inv
                    des_total = formatLang(self.env, des_inv + 0.0)
                    des_all = 'الايرادات المستحقة: ' + str(des_total) + '\n'

                    totall_all += late_unpaid_inv + partial_unpaid_inv + draft_unpaid_inv
                    all_total = formatLang(self.env, totall_all)
                    all_tot = 'مجموع المبالغ الغير محصلة: ' + str(all_total) + '\n'


                message = bank_info + 'الإجمالي بدون الضرائب: ' + str(total) + '\n'  + '\n' + des_all + '\n' + unpaid_all + '\n' + partial_all + '\n' + drafts_all + '\n' + all_tot 
                chat_id = company.bank_telegram
                token = company.telegram_token
                send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                send_text = send + message
                response = requests.post(send_text)
                
                
                
                
class employees(models.Model):
    _inherit = 'hr.employee'
    
    telegram_exp_move = fields.Text(compute='_get_telegram_exp_move', groups="hr.group_hr_user")

    def _get_telegram_exp_move(self):
        for employee in self:
            exp_move = False
            name = employee.name
            all_exp = ''
            move_amount = 0
            rev_amount = 0
            all_rev = 0
            total_exp_move = '0.00'
            if employee.all_exp:
                all_exp = formatLang(self.env, employee.all_exp)
            if employee.move_amount:
                move_amount = employee.move_amount
            if employee.rev_amount:
                rev_amount = employee.rev_amount
            if employee.total_exp_move:
                total_exp_move = formatLang(self.env, employee.total_exp_move)
            all_rev = move_amount + rev_amount
            all_rev_str = formatLang(self.env, all_rev)
            exp_move = name + ':' + '\n' + 'المصروفات: ' + all_exp + '\n' + 'الإيرادات: ' + all_rev_str + '\n' + 'صافي الربح/الخسارة: ' + total_exp_move
            employee.telegram_exp_move = exp_move


    def tele_total_exp_move(self):
        employees = self.env['hr.employee'].sudo().search([('telegram_exp_move','!=', False)])
        all_total_partner = ''
        all_total_employee = ''
        exp_employee = 0.0
        exp_partner = 0.0
        rev_employee = 0.0
        rev_partner = 0.0
        all_exp_partner = 0.0
        all_exp_employee = 0.0
        all_rev_partner = 0.0
        all_rev_employee = 0.0
        total_exp_move_partner = ''
        total_exp_move_employee = ''
        for employee in employees:
            company = employee.company_id
            if employee.telegram_exp_move:
                if employee.is_company_partner:
                    all_total_partner += employee.telegram_exp_move + '\n' + '\n'
                    if employee.all_exp:
                        exp_partner += employee.all_exp
                    rev_partner += (employee.move_amount or 0.0) + (employee.rev_amount or 0.0)
                else:
                    all_total_employee += employee.telegram_exp_move + '\n' + '\n'
                    if employee.all_exp:
                        exp_employee += employee.all_exp
                    rev_employee += (employee.move_amount or 0.0) + (employee.rev_amount or 0.0)

        total_exp_move_partner += all_total_partner
        total_exp_move_employee += all_total_employee
        all_exp_partner += exp_partner
        all_exp_employee += exp_employee
        all_rev_partner += rev_partner
        all_rev_employee += rev_employee
        if company.bank_telegram and company.telegram_token:
            partners = 'الشركاء:' + '\n' + total_exp_move_partner + '\n'  + 'مجموع المصروفات للشركاء: ' + str(formatLang(self.env, all_exp_partner)) + '\n'  + 'مجموع الإيرادات للشركاء: '  + str(formatLang(self.env, all_rev_partner))
            employeesm = 'الموظفين:' + '\n' + total_exp_move_employee + '\n'  + 'مجموع المصروفات للموظفين: ' + str(formatLang(self.env, all_exp_employee)) + '\n'  + 'مجموع الإيرادات للموظفين: '  + str(formatLang(self.env, all_rev_employee))
            message = 'الإيرادات والمصروفات' + '\n'  + '\n' + partners + '\n' + '\n' + employeesm 
            chat_id = company.bank_telegram
            token = company.telegram_token
            send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
            send_text = send + message
            response = requests.post(send_text)