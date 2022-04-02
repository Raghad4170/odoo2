# Copyright to The City Law Firm
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
import requests
import pytz
from dateutil.relativedelta import relativedelta
from odoo.http import Controller, request, route
from odoo import http, _
    
class MyAttendance(http.Controller):
    
    @http.route(['/my/sign_in_attendance'], type='http', auth="user", website=True)
    def sign_in_attendace(self, **post):
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        check_in = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = False
        if employee:
            just_checked_out = request.env['hr.attendance'].sudo().search([('employee_id','=',employee.id),('check_in', '<', datetime.now()), ('check_out', '<', datetime.now())], order='create_date desc', limit=1)
            if just_checked_out:
                time_check_out_s = datetime.now() - just_checked_out.check_out
                time_check_out = time_check_out_s.total_seconds() / 60
                if time_check_out <= 5:
                    return request.render('avatar.sign_attendance_error', {'time_check_in':'لا يمكنك تسجيل الدخول بعد تسجيل خروجك بأقل من ٥ دقائق'})
                else:
                    vals = {
                            'employee_id': employee.id,
                            'check_in': check_in,
                            }
                    attendance = request.env['hr.attendance'].sudo().create(vals)
                    if employee.company_id.telegram_token and employee.company_id.attendance_telegram:
                        message = 'تسجيل دخول ' + employee.name
            else:
                vals = {
                        'employee_id': employee.id,
                        'check_in': check_in,
                        }
                attendance = request.env['hr.attendance'].sudo().create(vals)
                if employee.company_id.telegram_token and employee.company_id.attendance_telegram:
                    message = 'تسجيل دخول ' + employee.name
            if message:
                chat_id = employee.company_id.attendance_telegram
                token = employee.company_id.telegram_token
                send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                send_text = send + message
                response = requests.post(send_text)
        return request.redirect('/my')


    @http.route(['/my/sign_out_attendance'], type='http', auth="user", website=True)
    def sign_out_attendace(self, **post):
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        message = False
        if employee:
            just_checked_in = request.env['hr.attendance'].sudo().search([('employee_id','=',employee.id),('check_in', '<', datetime.now()), ('check_in', '>', datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))], order='create_date desc',limit=1)
            if just_checked_in:
                time_check_in_s = datetime.now() - just_checked_in.check_in
                time_check_in = time_check_in_s.total_seconds() / 60
                if time_check_in <= 5:
                    return request.render('avatar.sign_attendance_error', {'time_check_in':'لا يمكنك تسجيل الخروج بعد تسجيل دخولك بأقل من ٥ دقائق'})
                else:
                    no_check_out_attendances = request.env['hr.attendance'].search([
                                ('employee_id', '=', employee.id),
                                ('check_out', '=', False),
                            ])
                    check_out = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
                    attendance = no_check_out_attendances.write({'check_out':check_out})
                    if employee.company_id.telegram_token and employee.company_id.attendance_telegram:
                        message = 'تسجيل خروج ' + employee.name
            else:
                no_check_out_attendances = request.env['hr.attendance'].search([
                            ('employee_id', '=', employee.id),
                            ('check_out', '=', False),
                        ])
                check_out = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
                attendance = no_check_out_attendances.write({'check_out':check_out})
                if employee.company_id.telegram_token and employee.company_id.attendance_telegram:
                    message = 'تسجيل خروج ' + employee.name
            if message:
                chat_id = employee.company_id.attendance_telegram
                token = employee.company_id.telegram_token
                send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                send_text = send + message
                response = requests.post(send_text)
        return request.redirect('/my')






class employeesinfo(models.Model):
    _inherit = 'hr.employee'

    def _attendance_action_change(self):
        res = super()._attendance_action_change()
        location = self.env.context.get('attendance_location', False)
        attendance_location = ''
        for employee in self:
            if employee.company_id.telegram_token and employee.company_id.attendance_telegram:
                name = employee.name
                message = ''
                if location: 
                    map = ("https://www.google.com/maps/search/{latitude},{longitude}/@{latitude},{longitude}".format(latitude=location[0],longitude=location[1]))
                    attendance_location = 'من الموقع:' + '\n' + map
                if employee.attendance_state == 'checked_in':
                    message = 'تسجيل دخول ' + name + '\n' + attendance_location
                else:
                    message = 'تسجيل خروج ' + name + '\n' + attendance_location
                chat_id = employee.company_id.attendance_telegram
                token = employee.company_id.telegram_token
                send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                send_text = send + message
                response = requests.post(send_text)
        return res

    todays_worked_hours = fields.Char(groups="hr.group_hr_user", compute="tele_todays_worked_hourss")
    checked_in = fields.Char(groups="hr.group_hr_user", compute="tele_todays_worked_hourss")
    checked_in_trial = fields.Char(groups="hr.group_hr_user")


    def tele_todays_worked_hourss(self):
        for employee in self:
            total_work = 0
            total_working_hours = 0
            data = self.env['hr.attendance'].sudo().search([('employee_id','=',employee.id),('check_in', '<=', datetime.now()), ('check_in', '>=', datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))])
            for attendance in data:
                total_work += attendance.worked_hours
                total_working_hours = timedelta(hours=total_work)
            checked = self.env['hr.attendance'].sudo().search([('employee_id','=',employee.id),('check_in', '<=', datetime.now()), ('check_in', '>=', datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))], order='check_in asc', limit=1)
            if checked.check_in:
                dt = pytz.timezone('UTC').localize(checked.check_in).astimezone(pytz.timezone(self.env.user.tz))
                str_time = dt.strftime("%H:%M:%S")
                check_in_date = datetime.strptime(str_time, "%H:%M:%S").time()
            else:
                check_in_date = 'لم يحضر'
            employee.checked_in = str(check_in_date)
            employee.todays_worked_hours = total_working_hours      
            
    is_holiday = fields.Boolean(compute="_check_employee_off_day")
    off_day = fields.Boolean(compute="_check_employee_off_day")
    
    def _check_employee_off_day(self):
        for employee in self:
            leave_obj = self.env['hr.leave']
            today_week_day = datetime.now().weekday()
            off_day = False
            is_holiday = False
            if employee.contract_id and employee.contract_id.state == 'open':
                today_official_leave=False
                for attendance_day_data in employee.resource_calendar_id.attendance_ids:
                      if attendance_day_data.dayofweek  == str(today_week_day):
                          today_official_leave=True
                if today_official_leave:
                    att_recs = leave_obj.search([('request_date_from', '<=', datetime.now()),
                                    ('request_date_to', '>=', datetime.now()),
                                    ('employee_id', '=', employee.id),('state','=','validate')])
                    
                    if len(att_recs):
                        is_holiday = True

                else:
                    off_day = True
            employee.off_day = off_day
            employee.is_holiday = is_holiday 
                        
    didnt_attend_today = fields.Boolean(default=False, groups="hr.group_hr_user")

    def didnt_attend(self):
        employees = self.env['hr.employee'].sudo().search([])
        for employee in employees:
            if employee.user_id:
                work_schedule = employee.resource_calendar_id
                weekday = str(datetime.now().weekday())
                dt = pytz.timezone('UTC').localize(datetime.now()).astimezone(pytz.timezone(employee.user_id.tz))
                time_now = dt.strftime('%H:%M')
                for schedule in work_schedule.attendance_ids:
                    if schedule.dayofweek == weekday:
                        if schedule.day_period == 'morning':
                            work_from = schedule.hour_from
                            start_time = datetime.now().date() + relativedelta(hours=work_from, minutes=0, seconds=0)
                            start_time = start_time.strftime('%H:%M')
                if start_time:
                    if not employee.didnt_attend_today:
                        if not employee.off_day:
                            if not employee.is_holiday:
                                if employee.user_id.chat_id and employee.company_id.telegram_token and employee.contract_id and employee.contract_id.state == 'open' and employee.contract_id.flexible == False:
                                    if employee.attendance_state == 'checked_out':
                                        checked = self.env['hr.attendance'].sudo().search([('employee_id','=',employee.id),('check_in', '<=', datetime.now()), ('check_in', '>=', datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))])
                                        if not checked:
                                            if start_time <= time_now:
                                                employee.didnt_attend_today = True
                                                message = 'لوحظ تأخركم عن تسجيل الحضور في الموعد المحدد، نأمل تقديم طلب تصحيح حضور إذا كنتم متواجدين أو المبادرة بتقديم عذر الغياب لتلافي تطبيق لائحة الجزاءات.'
                                                chat_id = employee.user_id.chat_id
                                                token = employee.company_id.telegram_token
                                                send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                                                send_text = send + message
                                                response = requests.post(send_text)


    def didnt_checked_out(self):
        employees = self.env['hr.employee'].sudo().search([])
        for employee in employees:
            employee.didnt_attend_today = False
            if not employee.off_day or employee.is_holiday:
                if employee.user_id.chat_id and employee.company_id.telegram_token and employee.contract_id and employee.contract_id.state == 'open' and employee.contract_id.flexible == False:
                    if employee.attendance_state == 'checked_in':
                        message = 'لوحظ عدم تسجيلكم للخروج في وقت انتهاء الدوام؛ نأمل منكم تسجيل خروجكم في حالة انتهائكم من الدوام تلافياً من احتساب اليوم كغياب.'
                        chat_id = employee.user_id.chat_id
                        token = employee.company_id.telegram_token
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + message
                        response = requests.post(send_text)
                    

class Attendanceupdation(models.Model):
    _inherit = 'hr.attendance'
    
    def check_in_update_in_telegram(self):
        today = date.today()
        companies = self.env['res.company'].sudo().search([])
        for company in companies:
            if company.attendance_telegram and company.telegram_token:
                employee_hour = ''
                employee_hours = ''
                all_employees = ''
                employees = self.env['hr.employee'].sudo().search([('company_id', '=', company.id)])
                for employee in employees:
                    if employee.sudo().contract_id.state == 'open':
                        if employee.off_day:
                            employee_hour += ''
                        elif employee.is_holiday:
                            employee_hour += employee.name + ': ' + employee.checked_in + ' (اجازة)' + '\n'
                        else:
                            employee_hour += employee.name + ': ' + employee.checked_in + '\n'
                employee_hours +=  employee_hour
                if employee_hours == '':
                    return False
                else:
                    message = 'الحضور: ' + str(today) + '\n' + employee_hours
                    chat_id = company.attendance_telegram
                    token = company.telegram_token
                    send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                    send_text = send + message
                    response = requests.post(send_text)

    
    def update_in_telegram(self):
        today = date.today()
        companies = self.env['res.company'].sudo().search([])
        for company in companies:
            if company.attendance_telegram and company.telegram_token:
                employee_hour = ''
                employee_hours = ''
                all_employees = ''
                employees = self.env['hr.employee'].sudo().search([('company_id', '=', company.id)])
                for employee in employees:
                    if employee.sudo().contract_id.state == 'open':
                        if employee.off_day:
                            employee_hour += ''
                        elif employee.is_holiday:
                            employee_hour += employee.name + ': ' + employee.todays_worked_hours + ' (اجازة)' + '\n'
                        else:
                            employee_hour += employee.name + ': ' + employee.todays_worked_hours + '\n'

                employee_hours +=  employee_hour
                if employee_hours == '':
                    return False
                else:
                    message = 'ساعات عمل اليوم: ' + str(today) + '\n' + employee_hours
                    chat_id = company.attendance_telegram
                    token = company.telegram_token
                    send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                    send_text = send + message
                    response = requests.post(send_text)
                    
                    
                    
class Violationstele(models.Model):
    _inherit = 'violations.violations'

    def action_confirm(self):
        amount = 0
        message = ''
        for violations in self:
            if violations.company_id.attendance_telegram and violations.company_id.telegram_token:
                violations.write({'state': 'confirm'})
                if violations.warning_sent == False:
                    amount = violations.amount
                    if amount > 1:
                        message = ('تم إحالة ' + violations.employee_id.name +  ' إلى التحقيق الإداري' + '\n' + 'المخالفة: ' + violations.name + '\n'  + 'نوع الجزاء: ' + violations.penality_name 
                                   +  '\n' + 'تاريخ الجزاء: ' + str(violations.date) + '\n' + 'المستند من اللائحة الداخلية: ' + violations.violation.name) 
                    else:
                        message = ('تم إرسال الجزاء إلى ' + violations.employee_id.name + '\n' + 'المخالفة: ' + violations.name + '\n'  + 'نوع الجزاء: ' + violations.penality_name 
                                   +  '\n' + 'تاريخ الجزاء: ' + str(violations.date) + '\n' + 'المستند من اللائحة الداخلية: ' + violations.violation.name) 
                    chat_id = violations.company_id.attendance_telegram
                    token = violations.company_id.telegram_token
                    send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                    send_text = send + message
                    response = requests.post(send_text)
        return super(Violationstele, self).action_confirm()
    
class SessionsTelegram(models.Model):
    _inherit = 'session.session'


    @api.model_create_multi
    def create(self, list_value):
        sessions = super(SessionsTelegram, self).create(list_value)
        for session in sessions:
            if session.user_id.company_id.telegram_token and session.user_id.company_id.session_telegram:
                name = session.user_id.name
                if session.user_id.partner_id.parent_id.is_company:
                    name = session.user_id.name + ' من شركة ' + session.user_id.partner_id.parent_id.name 
                message = 'تسجيل دخول ' + name
                chat_id = session.user_id.company_id.session_telegram
                token = session.user_id.company_id.telegram_token
                send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                send_text = send + message
                response = requests.post(send_text)
        return sessions
