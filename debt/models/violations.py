# Copyright to The City Law Firm

from odoo import models, fields, api, _
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError
import pytz
import dateutil
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning
from datetime import datetime, timedelta, date
import requests
from dateutil.relativedelta import relativedelta
            
class Violations(models.Model):
    _name = 'violations.violations'
    _description = 'violations.violations'
    _order = "date desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    
    name = fields.Char(string='المخالفة')
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('confirm', 'للموافقة'),
        ('refuse', 'إعفاء'),
        ('suspend', 'معلقة'),
        ('approved', 'مؤكد')
        ], string='الحالة', readonly=True, tracking=True, copy=False, default='draft')
    violation = fields.Many2one("violations.type", string=" المخالفة", required=True, readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='الموظف',index=True, readonly=True,
                                  states={'draft': [('readonly', False)]}, tracking=True)
    company_id = fields.Many2one(related='employee_id.company_id')
    manager_id = fields.Many2one('hr.employee', string='المدير', readonly=True)
    report_note = fields.Text('تعليق الموارد البشرية')
    date = fields.Date(string='تاربخ المخالفة', index=True, copy=False, required=True, default=fields.Datetime.now)
    caliming_date = fields.Date(string='تاريخ الاستحقاق', compute="_get_caliming_date", store=True, readonly=False)
    count = fields.Float(string='تكرار الموظف للمخالفة', compute="_get_count", store=True)
    penality = fields.Char(string='الجزاء', compute="_get_penality", store=True)
    penality_name = fields.Char(string='نوع الجزاء', compute="_get_penality_name", store=True)
    amount = fields.Float(string="amount", compute="_get_amount", store=True)
    warning_sent = fields.Boolean(store=True)
    
    
    @api.depends('date')
    def _get_caliming_date(self):
        for violations in self:
            if violations.date:
                violations.caliming_date = violations.date

    def violation_wizard(self):       
        return {
            'name': 'Violations',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(False, 'form')] ,

            'res_model': 'violations.wizard',
      
            'type': 'ir.actions.act_window',
            'target': 'new',
        } 



    @api.depends('violation', 'employee_id', 'date')
    def _get_count(self):
        for violations in self:
            count = 0
            all_count = 0
            Violation_count = self.env['violations.violations'].search([('violation','=', violations.violation.id),
                                                                        ('employee_id','=', violations.employee_id.id),
                                                                        ('state','!=','refuse'),
                                                                        ('date','<=', violations.date)])
            for c in Violation_count:
                days = (violations.date - c.date).days
                if days < 180:
                    count = 1
                else:
                    count = 0
                all_count += count
            if all_count == 1:
                violations.count = 1
            elif all_count == 2:
                violations.count = 2
            elif all_count == 3:
                violations.count = 3
            elif all_count >= 4:
                violations.count = 4
            else:
                violations.count = 1
          
    @api.depends('count')
    def _get_penality(self):
        for violations in self:            
            count = violations.count
            if count == 1:
                if violations.violation.First_time == 'اخرى':
                    violations.penality = violations.violation.First_other
                elif violations.violation.First_time == 'انذار كتابي':
                    violations.penality = 'انذار كتابي'
                else:
                    violations.penality = violations.violation.First_penality
            elif count == 2:
                if violations.violation.Second_Time == 'اخرى':
                    violations.penality = violations.violation.Second_other
                if violations.violation.Second_Time == 'انذار كتابي':
                    violations.penality = 'انذار كتابي'
                else:
                    violations.penality =  violations.violation.Second_penality
            elif count == 3:
                if violations.violation.Third_time == 'اخرى':
                    violations.penality = violations.violation.Third_other
                if violations.violation.Third_time == 'انذار كتابي':
                    violations.penality = 'انذار كتابي'
                else:
                    violations.penality =  violations.violation.Third_penality
            elif count == 4:
                if violations.violation.Fourth_time == 'اخرى':
                    violations.penality = violations.violation.Fourth_other
                if violations.violation.Fourth_time == 'انذار كتابي':
                    violations.penality = 'انذار كتابي'
                else:
                    violations.penality = violations.violation.Fourth_penality
            else:
                violations.penality = 0
                
    @api.depends('count')
    def _get_penality_name(self):
        for violation in self:
            if violation.count == 1:
                if violation.violation.First_time == 'نسبة مئوية':
                    violation.penality_name = 'خصم ' + str(violation.penality) + '%' + ' من اليوم'
                elif violation.violation.First_time == 'يوم':
                    violation.penality_name = 'خصم ' + str(violation.penality) + ' يوم'
                else: 
                    violation.penality_name = violation.penality
            elif violation.count == 2:
                if violation.violation.Second_Time  == 'نسبة مئوية':
                    violation.penality_name = 'خصم ' + str(violation.penality) + '%' + ' من اليوم'
                elif violation.violation.Second_Time == 'يوم':
                    violation.penality_name = 'خصم ' + str(violation.penality) + ' يوم'
                else: 
                    violation.penality_name = violation.penality
            elif violation.count == 3:
                if violation.violation.Third_time == 'نسبة مئوية':
                    violation.penality_name = 'خصم ' + str(violation.penality) + '%' + ' من اليوم'
                elif violation.violation.Third_time == 'يوم':
                    violation.penality_name = 'خصم ' + str(violation.penality) + ' يوم'
                else: 
                    violation.penality_name = violation.penality
            elif violation.count == 4:
                if violation.violation.Fourth_time == 'نسبة مئوية':
                    violation.penality_name = 'خصم ' + str(violation.penality) + '%' + ' من اليوم'
                elif violation.violation.Fourth_time == 'يوم':
                    violation.penality_name = 'خصم ' + str(violation.penality) + ' يوم'
                else: 
                    violation.penality_name = violation.penality
        
    @api.depends('count')
    def _get_amount(self):
        for violations in self:
            if violations.count == 1:
                if violations.violation.First_time == 'نسبة مئوية':
                    violations.amount = int(violations.violation.First_penality)/100
                elif violations.violation.First_time == 'يوم':
                    violations.amount = int(violations.violation.First_penality)
                else: 
                    violations.amount = 0
            elif violations.count == 2:
                if violations.violation.Second_Time  == 'نسبة مئوية':
                    violations.amount = float(violations.violation.Second_penality)/100
                elif violations.violation.Second_Time == 'يوم':
                    violations.amount = float(violations.violation.Second_penality)
                else: 
                    violations.amount = 0
            elif violations.count == 3:
                if violations.violation.Third_time == 'نسبة مئوية':
                    violations.amount = float(violations.violation.Third_penality)/100
                elif violations.violation.Third_time == 'يوم':
                    violations.amount = float(violations.violation.Third_penality)
                else: 
                    violations.amount = 0
            elif violations.count == 4:
                if violations.violation.Fourth_time == 'نسبة مئوية':
                    violations.amount = float(violations.violation.Fourth_penality)/100
                elif violations.violation.Fourth_time == 'يوم':
                    violations.amount = float(violations.violation.Fourth_penality)
                else: 
                    violations.amount = 0

    def action_draft(self):
        self.write({'state': 'draft'})
        return True


    def action_confirm(self):
        amount = 0
        mail_template = ''
        message = ''
        for violations in self:
            violations.write({'state': 'confirm'})
            if violations.warning_sent == False:
                amount = violations.amount
                if amount > 1:
                    message = ('تم إحالة ' + violations.employee_id.name +  ' إلى التحقيق الإداري' + '\n' + 'المخالفة: ' + violations.name + '\n'  + 'نوع الجزاء: ' + violations.penality_name 
                               +  '\n' + 'تاريخ الجزاء: ' + str(violations.date) + '\n' + 'المستند من اللائحة الداخلية: ' + violations.violation.name) 
                    if violations.employee_id.gender == 'female':
                        mail_template = self.env.ref('debt.violation_more_female')
                    elif violations.employee_id.gender == 'male':
                        mail_template = self.env.ref('debt.violation_more_male')
                else:
                    message = ('تم إرسال الجزاء إلى ' + violations.employee_id.name + '\n' + 'المخالفة: ' + violations.name + '\n'  + 'نوع الجزاء: ' + violations.penality_name 
                               +  '\n' + 'تاريخ الجزاء: ' + str(violations.date) + '\n' + 'المستند من اللائحة الداخلية: ' + violations.violation.name) 
                    if violations.employee_id.gender == 'female':
                        mail_template = self.env.ref('debt.violation_female')
                    elif violations.employee_id.gender == 'male':
                        mail_template = self.env.ref('debt.violation_male')
                mail_template.send_mail(violations.id, force_send=True, notif_layout='mail.mail_notification_light')
                send_mail=True
                violations.write({'warning_sent': True})   
                chat_id = '-466757622'
                token = '1754533305:AAHU1GE7qnQ2ouKY0SMPIPYipZOvqgYf97g'
                send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                send_text = send + message
                response = requests.post(send_text)


    def action_approve(self):
        for violations in self:
            violations.write({'state': 'approved'})
        
    def action_refuse(self):
        for violations in self:
            violations.write({'state': 'refuse'})
            
    def action_suspend(self):
        for violations in self:
            violations.write({'state': 'suspend'})
  
    def unlink(self):
        for violations in self:
            if violations.state == 'approved':
                raise UserError(('لا يمكنك حذف مخالفة تم تأكيدها!'))
            if violations.state == 'refuse':
                raise UserError(('لا يمكنك حذف مخالفة معفي عنها!'))
        result = super(Violations, self).unlink()
        return result

                        
    def check_send_email(self):
        employees = self.env['hr.employee'].sudo().search([])
        amount = 0
        mail_template = ''
        for employee in employees:
            if employee.sudo().contract_id.state == 'open':
                violations = self.env['violations.violations'].sudo().search([('employee_id','=', employee.id),
                                                                              ('warning_sent','=', False),
                                                                              ('state','in', ('confirm','approved'))])
                for violation in violations:
                    amount = violation.amount
                    if amount > 1:
                        if employee.gender == 'female':
                            mail_template = self.env.ref('debt.violation_more_female')
                        elif employee.gender == 'male':
                            mail_template = self.env.ref('debt.violation_more_male')
                    else:
                        if employee.gender == 'female':
                            mail_template = self.env.ref('debt.violation_female')
                        if employee.gender == 'male':
                            mail_template = self.env.ref('debt.violation_male')
                    mail_template.send_mail(violation.id, force_send=True, notif_layout='mail.mail_notification_light')
                    send_mail=True
                    violation.write({
                            'warning_sent': True
                        })                    
                    
class violationsWizard(models.TransientModel):
    _name = 'violations.wizard'
    _description = 'إنشاء المخالفات'

    date_from = fields.Date('من', required=True)
    date_to = fields.Date('إلى', required=True)

    def create_penality(self):
        work_entry_obj=self.env['hr.work.entry']
        new_date_from=datetime.strptime(self.date_from.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        new_date_to=datetime.strptime((self.date_to + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), DEFAULT_SERVER_DATETIME_FORMAT)
        old_violations = self.env['violations.violations'].sudo().search([
            ('date', '<=', datetime.strptime((self.date_to).strftime('%Y-%m-%d %H:%M:%S'), DEFAULT_SERVER_DATETIME_FORMAT)),
            ('date', '>=', new_date_from)])
        old_violations.unlink()
        todays_work_entries = work_entry_obj.sudo().search([('date_start','>=',new_date_from),('date_stop','<=',new_date_to),('name','ilike','متأخر')])
        for work_entry in todays_work_entries:
            difference = work_entry.date_stop - work_entry.date_start
            difference_minutes = difference.seconds / 60
            difference_all = timedelta(minutes=difference_minutes)
            date_work_entry = datetime.strptime(work_entry.date_start.strftime('%Y-%m-%d'), '%Y-%m-%d').date()
            if difference_minutes > 60:
                        record = self.env['violations.violations'].sudo().create({
                        'name': "تأخر لمدة: %s" % (difference_all),
                        'violation': self.env['violations.type'].search([('violation_type', '=', 'late_more_60m')])[0].id,
                        'employee_id': work_entry.employee_id.id,
                        'date': date_work_entry,
                    })
            elif difference_minutes > 30:
                record = self.env['violations.violations'].sudo().create({
                    'name': "تأخر لمدة: %s" % (difference_all),
                    'violation': self.env['violations.type'].search([('violation_type', '=', 'late_60m')])[0].id,
                    'employee_id': work_entry.employee_id.id,
                    'date': date_work_entry,
                })
            elif difference_minutes > 15:
                record = self.env['violations.violations'].sudo().create({
                    'name': "تأخر لمدة: %s " % (difference_all),
                    'violation': self.env['violations.type'].search([('violation_type', '=', 'late_30m')])[0].id,
                    'employee_id': work_entry.employee_id.id,
                    'date': date_work_entry,
                })
            elif difference_minutes > 1:
                record = self.env['violations.violations'].sudo().create({
                    'name': "تأخر لمدة: %s" % (difference_all),
                    'violation': self.env['violations.type'].search([('violation_type', '=', 'late_15m')])[0].id,
                    'employee_id': work_entry.employee_id.id,
                    'date': date_work_entry,
                })

        todays_early_work_entries = work_entry_obj.sudo().search([('date_start','>=',new_date_from),('date_stop','<=',new_date_to),('name','ilike','خروج مبكر')])
        for work_entry in todays_early_work_entries:
            difference=work_entry.date_stop - work_entry.date_start
            difference_minutes = difference.seconds / 60
            difference_all = timedelta(minutes=difference_minutes)
            date_work_entry = datetime.strptime(work_entry.date_start.strftime('%Y-%m-%d'), '%Y-%m-%d').date()
            if difference_minutes > 15:
                    record = self.env['violations.violations'].sudo().create({
                        'name': "خروج مبكر لمدة: %s" % (difference_all),
                        'violation': self.env['violations.type'].search([('violation_type', '=', 'early_more_15')])[0].id,
                        'employee_id':  work_entry.employee_id.id,
                        'date': date_work_entry,
                    })
            elif difference_minutes > 1:
                    record = self.env['violations.violations'].sudo().create({
                        'name': "خروج مبكر لمدة: %s" % (difference_all),
                        'violation': self.env['violations.type'].search([('violation_type', '=', 'early_15')])[0].id,
                        'employee_id': work_entry.employee_id.id,
                        'date': date_work_entry,
                })
                    
        todays_not_there_work_entries = work_entry_obj.sudo().search([('date_start','>=',new_date_from),('date_stop','<=',new_date_to),('name','ilike','غير متواجد')])
        for work_entry in todays_not_there_work_entries:
            difference=work_entry.date_stop - work_entry.date_start
            difference_minutes = difference.seconds / 60
            difference_all = timedelta(minutes=difference_minutes)
            date_work_entry = datetime.strptime(work_entry.date_start.strftime('%Y-%m-%d'), '%Y-%m-%d').date()
            if difference_minutes > 15:
                    record = self.env['violations.violations'].sudo().create({
                        'name': "خروج مبكر لمدة: %s" % (difference_all),
                        'violation': self.env['violations.type'].search([('violation_type', '=', 'early_more_15')])[0].id,
                        'employee_id':  work_entry.employee_id.id,
                        'date': date_work_entry,
                    })
            elif difference_minutes > 1:
                    record = self.env['violations.violations'].sudo().create({
                        'name': "خروج مبكر لمدة: %s" % (difference_all),
                        'violation': self.env['violations.type'].search([('violation_type', '=', 'early_15')])[0].id,
                        'employee_id': work_entry.employee_id.id,
                        'date': date_work_entry,
                })

        absence_work_entries = work_entry_obj.sudo().search([('date_start','>=',new_date_from),('date_stop','<=',new_date_to),('name','ilike',('غائب'))])
        absence_entries_count = False
        for work_entry in absence_work_entries:

            period_dic_morning=self.get_date_start_stop(work_entry.employee_id,datetime.strptime(work_entry.date_start.strftime('%Y-%m-%d'), '%Y-%m-%d').date(),"morning")
            period_dic_noon=self.get_date_start_stop(work_entry.employee_id,datetime.strptime(work_entry.date_start.strftime('%Y-%m-%d'), '%Y-%m-%d').date(),"afternoon")

            date_work_entry = datetime.strptime(work_entry.date_start.strftime('%Y-%m-%d'), '%Y-%m-%d').date()
            start_date_work_entry = datetime.strptime(work_entry.date_start.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

            stop_date_work_entry = datetime.strptime(work_entry.date_stop.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
           
            noon_absence_entries_count = work_entry_obj.sudo().search([('date_start','>=',period_dic_noon['start_date_not_str']),('date_stop','<=',period_dic_noon['end_date_not_str']),('name','ilike','غائب'),('employee_id','=', work_entry.employee_id.id)])

            morning_absence_entries_count = work_entry_obj.sudo().search([('date_start','>=',period_dic_morning['start_date_not_str']),('date_stop','<=',period_dic_morning['end_date_not_str']),('name','ilike','غائب'),('employee_id','=', work_entry.employee_id.id)])
           
            if len(noon_absence_entries_count) + len(morning_absence_entries_count) ==2:
                    
                    existed=self.env['violations.violations'].sudo().search([('name','=', "غياب يوم %s" % str(date_work_entry)),('violation','=',self.env['violations.type'].search([('violation_type', '=', 'absence')])[0].id),('employee_id','=',work_entry.employee_id.id),('date','=',date_work_entry)])
                    if not len(existed):
                        record = self.env['violations.violations'].sudo().create({
                            'name': "غياب يوم %s" % str(date_work_entry),
                            'violation': self.env['violations.type'].search([('violation_type', '=', 'absence')])[0].id,
                            'employee_id': work_entry.employee_id.id,
                            'date': date_work_entry,
                        })
                   
            elif len(morning_absence_entries_count) <= 1 and not len(noon_absence_entries_count):
                difference=work_entry.date_stop - work_entry.date_start
                difference_minutes = difference.seconds / 60
                difference_all = timedelta(minutes=difference_minutes)
                record = self.env['violations.violations'].sudo().create({
                    'name': "تأخر لمدة: %s" % (difference_all),
                    'violation': self.env['violations.type'].search([('violation_type', '=', 'late_more_60m')])[0].id,
                    'employee_id': work_entry.employee_id.id,
                    'date': date_work_entry,
                })
        

            elif len(noon_absence_entries_count) <= 1 and not len(morning_absence_entries_count):
                difference=work_entry.date_stop - work_entry.date_start
                difference_minutes = difference.seconds / 60
                difference_all = timedelta(minutes=difference_minutes)                
                record = self.env['violations.violations'].sudo().create({
                    'name': "خروج مبكر لمدة: %s" % (difference_all),
                    'violation': self.env['violations.type'].search([('violation_type', '=', 'early_more_15')])[0].id,
                    'employee_id': work_entry.employee_id.id,
                    'date': date_work_entry,
                })

        return {
    'type': 'ir.actions.client',
    'tag': 'reload',
}

    def get_date_start_stop(self,emp,date_today,day_period):
        date_dic = {}
        x = date.today()
        today_week_day =date_today.weekday()
        old_tz = pytz.timezone('UTC')
        new_tz = pytz.timezone(self.env.user.tz)
   
        emps=self.env['hr.employee'].browse(emp)

        if emp.contract_id and emp.contract_id.state == 'open':

            for attendance_day_data in emp.resource_calendar_id.attendance_ids:
                  

                    if attendance_day_data.dayofweek  == str(today_week_day):
                        if attendance_day_data.day_period==day_period:
                            start_date = date_today+relativedelta(hours=attendance_day_data.hour_from, minutes=0, seconds=0)
                            date_dic['start_date_not_str']=datetime.strptime(new_tz.localize(start_date).astimezone(old_tz).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')

                            start_date =  fields.Datetime.to_string(new_tz.localize(start_date).astimezone(old_tz))
                            date_dic['start_date']=start_date
                            
                            end_date = date_today+relativedelta(hours=attendance_day_data.hour_to, minutes=0, seconds=0)
                            date_dic['end_date_not_str']=datetime.strptime(new_tz.localize(end_date).astimezone(old_tz).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')

                            end_date = fields.Datetime.to_string(new_tz.localize(end_date).astimezone(old_tz))
                            date_dic['end_date']=end_date
                            if day_period=='morning':
                                   end_date = date_today+relativedelta(hours=attendance_day_data.hour_to, minutes=60, seconds=0)
                                   date_dic['end_date_not_str_plus_break']=datetime.strptime(new_tz.localize(end_date).astimezone(old_tz).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')

                                

                            date_dic['holiday']=False
        if self.check_leave(date_today,emps.id):
                date_dic['holiday']=True
                return date_dic

        if not date_dic.get("start_date",False):
                date_dic['holiday']=True


        return date_dic
    
    def check_leave(self,date_today,emp):
        leave_obj=self.env['hr.leave']
        att_recs = leave_obj.search([('request_date_from', '<=', date_today),
                                    ('request_date_to', '>=', date_today),
                                    ('employee_id', '=', emp.id),('state','=','validate')])

        if len(att_recs) : 

            return True
        else:
            return False   
