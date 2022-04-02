# Copyright to The City Law Firm
from odoo import models, fields, api, _, exceptions
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta, date
from odoo.exceptions import AccessError, UserError, ValidationError
import pytz
import logging
import dateutil
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    kiosk_employee = fields.Boolean(string="حضور بالكشك", groups="base.group_user")

    attendance_state = fields.Selection(groups="base.group_user")

    hours_today = fields.Float(groups="base.group_user")

    
    def _attendance_action_change(self):
        res = super()._attendance_action_change()
        for employee in self:
            just_checked_in = self.env['hr.attendance'].sudo().search([('employee_id','=',employee.id),('check_in', '<', datetime.now()), ('check_in', '>', datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')), ('check_out', '<', datetime.now())], order='create_date desc',limit=1)
            if just_checked_in:
                if self.attendance_state == 'checked_out':
                    time_check_in_s = datetime.now() - just_checked_in.check_in
                    time_check_in = time_check_in_s.total_seconds() / 60
                    if time_check_in <= 5:
                        raise exceptions.UserError(_('لا يمكنك تسجيل الخروج بعد تسجيل دخولك بأقل من ٥ دقائق'))

            just_checked_out = self.env['hr.attendance'].sudo().search([('employee_id','=',employee.id),('check_in', '<', datetime.now()), ('check_out', '<', datetime.now())], order='create_date desc', limit=1)
            if just_checked_out:
                if employee.attendance_state != 'checked_out':
                    time_check_in_s = datetime.now() - just_checked_out.check_out
                    time_check_in = time_check_in_s.total_seconds() / 60
                    if time_check_in <= 5:
                        raise exceptions.UserError(_('لا يمكنك تسجيل الدخول بعد تسجيل خروجك بأقل من ٥ دقائق'))
        return res


    

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    attendance_state = fields.Selection(groups="base.group_user")
    
    kiosk_employee = fields.Boolean(groups="base.group_user")

    hours_today = fields.Float(groups="base.group_user")

class HrContracttype(models.Model):
    _inherit = 'hr.contract.type'

    flexible = fields.Boolean(string="دوام مرن")

class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    flexible = fields.Boolean(string="دوام مرن", related='contract_type_id.flexible')

class AttendanceViolations(models.Model):
    _inherit = 'hr.attendance'

    day_period_m = fields.Selection([('morning', 'Morning'), ('afternoon', 'afternoon')], compute="cday_period_m",store=True)

    early_exit = fields.Integer(string="Early Check-out(Minutes)")
    late_check_in = fields.Integer(string="Late Check-in(Minutes)")
    run_from_cron=fields.Boolean(string="cron_run",compute="_run_from_cron")
    no_break=fields.Boolean(string="No Break",compute="_compute_no_break")
    break_from=fields.Datetime(string="Break From",compute="_compute_break")
    break_to=fields.Datetime(string="Break To",compute="_compute_break")
    day_period = fields.Selection(selection=[('morning', 'Morning'),
                                             ('afternoon', 'Afternoon')],
                                  string="Day Period", compute="onchange_check_in", readonly=False)
 

#############################################manali#####################################################
    def _compute_no_break(self):
        for att in self:
            logging.info(" att.check_out%s__??????????????????????????????????", att.check_out)
            logging.info("att.break_from%s__??????????????????????????????????",att.break_from)
            logging.info("att.check_in%s__??????????????????????????????????",att.check_in)
            logging.info("att.break_to%s__??????????????????????????????????",att.break_to)
            logging.info("att%s__??????????????????????????????????",att)
            if att.break_from == False:
                att.no_break = False

                continue   
            if att.check_out == False:
                att.no_break = False

                continue
            if att.break_to == False:
                att.no_break = False

                continue
            if att.check_in == False:
                att.check_in = False

                continue            

            # if att.check_in < att.break_from and att.check_out > att.break_to :
            #     att.no_break = True
            # else:
            #     att.no_break = False
            att.no_break = False

            if att.check_out > att.break_from and att.check_in< att.break_from and att.check_out > att.break_to :
                att.no_break = True
            else:
                att.no_break = False
            if att.check_in > att.break_from and att.check_out< att.break_to :
                att.no_break = True
            else:
                att.no_break = False
            if att.check_in < att.break_from and att.check_out > att.break_to :
                att.no_break = True

            

    def _compute_break(self):
        for att in self:
            
            x = att.check_in.date()

            today_week_day =date.today().weekday()
            logging.info("today_week_day%s__----------------",today_week_day)
            if today_week_day==4:
                today_week_day=3

            old_tz = pytz.timezone('UTC')
            new_tz = pytz.timezone(self.env.user.tz)
            emp=att.employee_id
            att.break_from=None
            att.break_to=None

            for attendance_day_data in emp.resource_calendar_id.attendance_ids:
                    if attendance_day_data.dayofweek  == str(today_week_day):
                        if attendance_day_data.day_period == 'afternoon':
                            start_date= x+relativedelta(hours=attendance_day_data.hour_from, minutes=0, seconds=0)
                            att.break_to =datetime.strptime(new_tz.localize(start_date).astimezone(old_tz).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')

                        if attendance_day_data.day_period == 'morning':
                                brk_from = x+relativedelta(hours=attendance_day_data.hour_to, minutes=0, seconds=0)
                                att.break_from =datetime.strptime(new_tz.localize(brk_from).astimezone(old_tz).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')

      
    def _run_from_cron(self):
        for att in self:
            att.run_from_cron = True
    def check_leave(self,date_today,emp):
        leave_obj=self.env['hr.leave']
        #logging.info("date_today%s__??????????????????????????????????",date_today)

        att_recs = leave_obj.search([('request_date_from', '<=', date_today),
                                    ('request_date_to', '>=', date_today),
                                    ('employee_id', '=', emp.id),('state','=','validate'),('request_unit_hours','=',False),('request_unit_half','=',False)])

        if len(att_recs) : 

            return True
        else:
            return False        

    def check_leave_detail(self,date_today,emp):
        leave_obj=self.env['hr.leave']
        dic={}
        #logging.info("date_today%s__??????????????????????????????????",date_today)

        att_recs = leave_obj.search([('request_date_from', '<=', date_today),
                                    ('request_date_to', '>=', date_today),
                                    ('employee_id', '=', emp.id),('state','=','validate')])

        if len(att_recs) : 

            for rec in att_recs:
                if rec.request_unit_half:
                    dic['leave_type']='half_day'
                    dic['leave_period']=rec.request_date_from_period
                    dic['leave_entry_type']=rec.holiday_status_id.work_entry_type_id

                elif rec.request_unit_hours:
                    dic['leave_type']='custom_hours'
                    dic['leave_hour_from']=rec.request_hour_from
                    dic['leave_hour_to']=rec.request_hour_to
                    dic['leave_entry_type']=rec.holiday_status_id.work_entry_type_id



                else:
                    dic['leave_type']='full_days'                  
                    dic['leave_entry_type']=rec.holiday_status_id.work_entry_type_id

            return dic
        else:
            dic['leave_type']='no_leave'
            return dic

#
    def send_mail_to_uncheckedout_employees(self):
        x = date.today()
        today_week_day =date.today().weekday()
        old_tz = pytz.timezone('UTC')
        new_tz = pytz.timezone(self.env.user.tz)
        employees = self.env['hr.employee'].sudo().search([])
        for emp in employees:
            if emp.sudo().contract_id and emp.sudo().contract_id.state == 'open' and emp.sudo().contract_id.flexible == False:
                send_mail=False
                for attendance_day_data in emp.resource_calendar_id.attendance_ids:
                    if attendance_day_data.dayofweek  == str(today_week_day):
                        # if attendance_day_data.day_period == 'afternoon':
                            start_date = x+relativedelta(hours=attendance_day_data.hour_from, minutes=0, seconds=0)
                            if self.check_leave(start_date,emp):
                                    continue
                            start_date_object=datetime.strptime(new_tz.localize(start_date).astimezone(old_tz).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')
                            #logging.info("today start_date_object%s------------",start_date_object)
                            #logging.info("today x%s------------",x)

                            #logging.info("today start_date_object%s------------",datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))

                            today_attandance_records = self.env['hr.attendance'].sudo().search([('check_in', '>=',x),('is_trip_entry','=',False),('check_out','=',False),('employee_id','=',emp.id)])
                            if send_mail == False:
                                if  len(today_attandance_records):
                                    if emp.gender == 'female':
                                        mail_template = self.env.ref('attendance.send_email_forgot_checkout_female')
                                        mail_template.send_mail(emp.id, force_send=True,notif_layout='mail.mail_notification_light')
                                        send_mail=True
                                    elif emp.gender == 'male':
                                        mail_template = self.env.ref('attendance.send_email_forgot_checkout_male')
                                        mail_template.send_mail(emp.id, force_send=True,notif_layout='mail.mail_notification_light')
                                        send_mail=True

                                 


                

        return True

    def send_mail_to_late_employees(self):
        x = date.today()
        today_week_day =date.today().weekday()
        old_tz = pytz.timezone('UTC')
        new_tz = pytz.timezone(self.env.user.tz)
        employees = self.env['hr.employee'].sudo().search([])
        for emp in employees:
            if emp.sudo().contract_id and emp.sudo().contract_id.state == 'open' and emp.sudo().contract_id.flexible == False:
                for attendance_day_data in emp.resource_calendar_id.attendance_ids:
                    if attendance_day_data.dayofweek  == str(today_week_day):
                        if attendance_day_data.day_period == 'morning':
                            start_date = x+relativedelta(hours=attendance_day_data.hour_from, minutes=10, seconds=0)
                            if self.check_leave(start_date,emp):
                                    continue
                            start_date_object=datetime.strptime(new_tz.localize(start_date).astimezone(old_tz).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')
                            #logging.info("today start_date_object%s------------",start_date_object)
                            #logging.info("today start_date_object%s------------",datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))

                            today_attandance_records = self.env['hr.attendance'].sudo().search([('check_in', '<=',start_date_object),('is_trip_entry','=',False),
                                                 ('check_in', '>=', datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')),('employee_id','=',emp.id)])
                            if not len(today_attandance_records):
                                if emp.gender == 'female':
                                    mail_template = self.env.ref('attendance.send_email_late_female')
                                    mail_template.send_mail(emp.id, force_send=True,notif_layout='mail.mail_notification_light')
                                elif emp.gender == 'male':
                                    mail_template = self.env.ref('attendance.send_email_late_male')
                                    mail_template.send_mail(emp.id, force_send=True,notif_layout='mail.mail_notification_light')
                                 


                

        return True
###########################################################################################################        

    @api.depends('day_period')
    def cday_period_m(self):
        for rec in self:
            rec.day_period_m=rec.day_period
                




    @api.onchange('check_in')
    @api.depends('check_in')
    def onchange_check_in(self):
        user_tz = self.env.user.tz
        for rec in self:
            check_in = rec.check_in
            if user_tz in pytz.all_timezones:
                old_tz = pytz.timezone('UTC')
                new_tz = pytz.timezone(user_tz)
                check_in = old_tz.localize(check_in).astimezone(new_tz)

            check_in_date = check_in.date()
            td_date = datetime.strptime(check_in_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                        DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(hours=9)

            #logging.info("td_date--------------------%s",td_date)
            #logging.info("rec.check_in--------------------%s",rec.check_in)
             
            if rec.check_in < td_date:
                rec.day_period = 'morning'
                print('Morninggggggggggggggggggggggggggg')
            elif rec.check_in > td_date:
                rec.day_period = 'afternoon'

                print('Afternooonnnnn')
    def check_multiple_entry_issue_no(self,employee_id,day_period):
        
      
        data= self.env['hr.attendance'].sudo().search([('employee_id','=',employee_id),('day_period_m','=',day_period),('is_trip_entry','=',False),('excuse_check_in','=',False),('excuse_check_out','=',False),('check_in', '<=', datetime.now()),('is_trip_entry','=',False),
                                            ('check_in', '>=', datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))], order='id asc')

        logging.info('*****************************************************-%s-----',data)
        previous_date=False
        previous_date_early=False
        previous_date_morning=False

        if len(data)>1:
            rec =data[-1]
            rec.late_check_in = 0.0
            rec.early_exit = 0.0
            week_day = rec.sudo().check_in.weekday()
            work_schedule = rec.sudo().employee_id.resource_calendar_id
            for schedule in work_schedule.sudo().attendance_ids:
                #logging.info('*****************************************************-%s-----',rec.day_period)

                if schedule.dayofweek == str(week_day):
                    if schedule.day_period == 'morning' and rec.day_period == 'morning':
                            work_to = schedule.hour_to
                            result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_to * 60, 60))

                            user_tz = self.env.user.tz
                            dt_in_utc = rec.check_in
                            dt_out_utc = rec.check_out
                            dt = rec.check_in
                            dt_out = rec.check_out
                            if user_tz in pytz.all_timezones:
                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                dt = old_tz.localize(dt).astimezone(new_tz)
                                dt_out = old_tz.localize(dt_out).astimezone(new_tz)

                            end_time = dt_out.strftime("%H:%M")
                            check_out_date = datetime.strptime(end_time, "%H:%M").time()
                            end_date = datetime.strptime(result, "%H:%M").time()
                            t1 = timedelta(hours=check_out_date.hour, minutes=check_out_date.minute)
                            t2 = timedelta(hours=end_date.hour, minutes=end_date.minute)
                            if check_out_date < end_date:
                                final = t2 - t1
                                rec.sudo().early_exit = final.total_seconds() / 60
                            #logging.info("check_out_date-------------%s--------",check_out_date)
                            #logging.info("end_date-------------%s--------",end_date)
                            if rec.early_exit > 0:
                                rec.sudo().early_exit = 0.0
                                end_display_date = dt_in_utc.date()+relativedelta(hours=work_to, minutes=0, seconds=0)
                                if self.check_leave(end_display_date,rec.employee_id):
                                    continue
                                end_display_date =  fields.Datetime.to_string(new_tz.localize(end_display_date).astimezone(old_tz))
                                if not rec.excuse_check_out:
                                    work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)
                                    if not  self.run_from_cron:

                                                record = self.env['hr.work.entry'].sudo().create({
                                                    'contract_id': rec.sudo().employee_id.contract_id.id,
                                                    'name': "خروج مبكر %s" % (rec.employee_id.name),
                                                    'date_start': dt_out_utc,
                                                    'date_stop': end_display_date,
                                                    'employee_id': rec.employee_id.id,
                                                    'work_entry_type_id': work_entry_type.id,
                                                })

                    if schedule.day_period == 'afternoon' and rec.day_period == 'afternoon':
                        work_to = schedule.hour_to
                        result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_to * 60, 60))
                        user_tz = self.env.user.tz
                        dt_in_utc = rec.check_in
                        dt_out_utc = rec.check_out
                        dt = rec.check_in
                        dt_out = rec.check_out
                        if user_tz in pytz.all_timezones:
                            old_tz = pytz.timezone('UTC')
                            new_tz = pytz.timezone(user_tz)
                            dt = old_tz.localize(dt).astimezone(new_tz)
                            dt_out = old_tz.localize(dt_out).astimezone(new_tz)

                        end_time = dt_out.strftime("%H:%M")
                        check_out_date = datetime.strptime(end_time, "%H:%M").time()
                        end_date = datetime.strptime(result, "%H:%M").time()
                        t1 = timedelta(hours=check_out_date.hour, minutes=check_out_date.minute)
                        t2 = timedelta(hours=end_date.hour, minutes=end_date.minute)
                        #logging.info("check_out_date-------------%s--------",dt_out_utc)
                        #logging.info("end_date-------------%s--------",check_out_date)

                        if check_out_date < end_date:
                            final = t2 - t1
                            rec.sudo().early_exit = final.total_seconds() / 60

                        if rec.early_exit > 0:
                            rec.sudo().early_exit = 0.0
                            end_display_date = dt_in_utc.date()+relativedelta(hours=work_to, minutes=0, seconds=0)
                            if self.check_leave(end_display_date,rec.employee_id):
                                continue
                            end_display_date =  fields.Datetime.to_string(new_tz.localize(end_display_date).astimezone(old_tz))
                            if not rec.excuse_check_out:
                                work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)
                                if not  self.run_from_cron:
                                            if previous_date_early!=False:
                                                start_date=previous_date_early
                                            if not rec.no_break:
                                                record = self.env['hr.work.entry'].sudo().create({
                                                    'contract_id': rec.sudo().employee_id.contract_id.id,
                                                    'name': "خروج مبكر %s" % (rec.employee_id.name),
                                                    'date_start': dt_out_utc,
                                                    'date_stop': end_display_date,
                                                    'employee_id': rec.employee_id.id,
                                                    'work_entry_type_id': work_entry_type.id,
                                                })
                 
 
            for rec in data:
                rec.late_check_in = 0.0
                rec.early_exit = 0.0
                week_day = rec.sudo().check_in.weekday()
                work_schedule = rec.sudo().employee_id.resource_calendar_id
                for schedule in work_schedule.sudo().attendance_ids:
                    #logging.info('*****************************************************-%s-----',rec.day_period)

                    if schedule.dayofweek == str(week_day):
                        if schedule.day_period == 'morning' and rec.day_period == 'morning':
                            work_from = schedule.hour_from
                            result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_from * 60, 60))

                            user_tz = self.env.user.tz
                            dt_in_utc = rec.check_in
                            dt_out_utc = rec.check_out
                            dt = rec.check_in
                            dt_out = rec.check_out
                            if user_tz in pytz.all_timezones:
                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                dt = old_tz.localize(dt).astimezone(new_tz)
                                #logging.info("rec-------------------------%s",rec.sudo().employee_id.contract_id)
                                #logging.info("rec-------------------------%s",rec)
                                #logging.info("date-------------------------%s",dt_out)
                                if not dt_out:
                                    continue
                                dt_out = old_tz.localize(dt_out).astimezone(new_tz)

                            str_time = dt.strftime("%H:%M")
                            check_in_date = datetime.strptime(str_time, "%H:%M").time()
                            start_date = datetime.strptime(result, "%H:%M").time()
                            t1 = timedelta(hours=check_in_date.hour, minutes=check_in_date.minute)
                            t2 = timedelta(hours=start_date.hour, minutes=start_date.minute)
                            if check_in_date > start_date:
                                final = t1 - t2
                                rec.sudo().late_check_in = final.total_seconds() / 60

                            if rec.late_check_in > 0:
                                rec.sudo().late_check_in = 0.0
                                work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)  

                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                start_date = dt_in_utc.date()+relativedelta(hours=work_from, minutes=0, seconds=0)
                                if self.check_leave(start_date,rec.employee_id):
                                    continue
                                start_date =  fields.Datetime.to_string(new_tz.localize(start_date).astimezone(old_tz))
                                #logging.info('work_from----------%s-----',start_date)
                                #logging.info('today_date.date----------%s-----',dt_in_utc.date())
                                #logging.info('dt_in_utc----------%s-----',dt_in_utc)
                                #logging.info('dt_out_utc----------%s-----',dt_out_utc)
                                end_date_as_par_contract =  dt_in_utc.date()+relativedelta(hours=schedule.hour_to, minutes=0, seconds=0)
                                end_date_as_par_contract_display = fields.Datetime.to_string(new_tz.localize(end_date_as_par_contract).astimezone(old_tz))
                                #logging.info('end_date_as_par_contractend_date_as_par_contract----------%s-----',end_date_as_par_contract)
                                if dt_in_utc < end_date_as_par_contract :
                                    if not rec.excuse_check_in:
                                        if not  self.run_from_cron:
                                            if previous_date_morning!=False:
                                                start_date=previous_date_morning

                                            record = self.env['hr.work.entry'].sudo().create({
                                                'contract_id': rec.sudo().employee_id.contract_id.id,
                                                'name': "غائب %s" % (rec.employee_id.name),
                                                'date_start':start_date,
                                                'date_stop': dt_in_utc ,
                                                'employee_id': rec.employee_id.id,
                                                'work_entry_type_id': work_entry_type.id,
                                            })
                            previous_date_morning=dt_out_utc




                        if schedule.day_period == 'afternoon' and rec.day_period == 'afternoon':
                            work_from = schedule.hour_from
                            result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_from * 60, 60))
                            user_tz = self.env.user.tz
                            dt_in_utc = rec.check_in
                            dt_out_utc = rec.check_out
                            
                            logging.info('dt_in_utc---ssssssssssss-------%s-----',dt_in_utc)
                            logging.info('dt_out_utc----ssssssssssssssssss------%s-----',dt_out_utc)
                            if dt_out_utc== False:
                                continue
                            dt = rec.check_in
                            if user_tz in pytz.all_timezones:
                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                dt = old_tz.localize(dt).astimezone(new_tz)
                            str_time = dt.strftime("%H:%M")
                            check_in_date = datetime.strptime(str_time, "%H:%M").time()
                            start_date = datetime.strptime(result, "%H:%M").time()

                            t1 = timedelta(hours=check_in_date.hour, minutes=check_in_date.minute)
                            t2 = timedelta(hours=start_date.hour, minutes=start_date.minute)
                            if check_in_date > start_date:
                                final = t1 - t2
                                rec.sudo().late_check_in = final.total_seconds() / 60

                            if rec.late_check_in > 0:
                                rec.sudo().late_check_in = 0.0
                                
                                work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)  

                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                start_date = dt_in_utc.date()+relativedelta(hours=work_from, minutes=0, seconds=0)
                                if self.check_leave(start_date,rec.employee_id):
                                    continue
                                start_date =  fields.Datetime.to_string(new_tz.localize(start_date).astimezone(old_tz))
                                logging.info('work_from----------%s-----',work_from)
                                logging.info('today_date.date----------%s-----',start_date)
                                logging.info('dt_in_utc----------%s-----',dt_in_utc)
                                logging.info('dt_out_utc----------%s-----',dt_out_utc)
                                #if contact end date time of day must be greater than check in time
                                end_date_as_par_contract =  dt_in_utc.date()+relativedelta(hours=schedule.hour_to, minutes=0, seconds=0)
                                logging.info('end_date_as_par_contractend_date_as_par_contract----------%s-----',end_date_as_par_contract)
                                if dt_in_utc < end_date_as_par_contract :
                                    if not rec.excuse_check_in:
                                        if not  self.run_from_cron:
                                                if previous_date!=False:
                                                    start_date=previous_date

                                                record = self.env['hr.work.entry'].sudo().create({
                                                    'contract_id': rec.sudo().employee_id.contract_id.id,
                                                    'name': "غائب%s" % (rec.employee_id.name),
                                                    'date_start':start_date,
                                                    'date_stop': dt_in_utc ,
                                                    'employee_id': rec.employee_id.id,
                                                    'work_entry_type_id': work_entry_type.id,
                                                })

                            previous_date=dt_out_utc

            return True
        else:
            return False


    def check_multiple_entry_issue(self,employee_id,day_period):
        
      
        data= self.env['hr.attendance'].sudo().search([('employee_id','=',employee_id),('day_period_m','=',day_period),('is_trip_entry','=',False),('excuse_check_in','=',False),('excuse_check_out','=',False),('check_in', '<=', datetime.now()),('is_trip_entry','=',False),
                                            ('check_in', '>=', datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))], order='id asc')

        if len(data)>1:
                return True
        else:
            return False

    def get_late_minutes(self):
        contract_running=self.env['hr.contract'].search([('state','=','open'),('flexible','=',False)])
        self.absent_employee()
        #logging.info("run_from_cron--||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||------------------%s",self.run_from_cron)
        for contract in contract_running:
            self.check_multiple_entry_issue_no(contract.employee_id.id,'morning')
            self.check_multiple_entry_issue_no(contract.employee_id.id,'afternoon')
            

        data = self.env['hr.attendance'].sudo().search([('check_in', '<=', datetime.now()),('is_trip_entry','=',False),
                                                 ('check_in', '>=', datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))])
        #logging.info("datetime.now()-------------------------%s",datetime.now())
        #logging.info("datetime.now()---datetime.strptime(date.today().str-------------------%s",datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))
        # if self.run_from_cron:
        #     return
        for rec in data:
            
            rec.late_check_in = 0.0
            rec.early_exit = 0.0
            week_day = rec.sudo().check_in.weekday()
            if rec.sudo().employee_id.contract_id and rec.sudo().employee_id.contract_id.state == 'open' and rec.sudo().employee_id.contract_id.flexible == False:
                work_schedule = rec.sudo().employee_id.resource_calendar_id
                for schedule in work_schedule.sudo().attendance_ids:
                    if schedule.dayofweek == str(week_day):
                        if schedule.day_period == 'morning' and rec.day_period == 'morning':
                            work_from = schedule.hour_from
                            result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_from * 60, 60))

                            user_tz = self.env.user.tz
                            dt_in_utc = rec.check_in
                            dt_out_utc = rec.check_out
                            dt = rec.check_in
                            dt_out = rec.check_out
                            if user_tz in pytz.all_timezones:
                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                dt = old_tz.localize(dt).astimezone(new_tz)
                                #logging.info("rec-------------------------%s",rec.sudo().employee_id.contract_id)
                                #logging.info("rec-------------------------%s",rec)
                                #logging.info("date-------------------------%s",dt_out)
                                if not dt_out:
                                    continue
                                dt_out = old_tz.localize(dt_out).astimezone(new_tz)

                            str_time = dt.strftime("%H:%M")
                            check_in_date = datetime.strptime(str_time, "%H:%M").time()
                            start_date = datetime.strptime(result, "%H:%M").time()
                            t1 = timedelta(hours=check_in_date.hour, minutes=check_in_date.minute)
                            t2 = timedelta(hours=start_date.hour, minutes=start_date.minute)
                            if check_in_date > start_date:
                                final = t1 - t2
                                rec.sudo().late_check_in = final.total_seconds() / 60

                            if rec.late_check_in > 0:
                                rec.sudo().late_check_in = 0.0
                                work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)  

                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                start_date = dt_in_utc.date()+relativedelta(hours=work_from, minutes=0, seconds=0)
                                if self.check_leave(start_date,rec.employee_id):
                                    continue
                                start_date =  fields.Datetime.to_string(new_tz.localize(start_date).astimezone(old_tz))
                                #logging.info('work_from----------%s-----',start_date)
                                #logging.info('today_date.date----------%s-----',dt_in_utc.date())
                                #logging.info('dt_in_utc----------%s-----',dt_in_utc)
                                #logging.info('dt_out_utc----------%s-----',dt_out_utc)
                                end_date_as_par_contract =  dt_in_utc.date()+relativedelta(hours=schedule.hour_to, minutes=0, seconds=0)
                                end_date_as_par_contract_display = fields.Datetime.to_string(new_tz.localize(end_date_as_par_contract).astimezone(old_tz))
                                #logging.info('end_date_as_par_contractend_date_as_par_contract----------%s-----',end_date_as_par_contract)
                                if dt_in_utc < end_date_as_par_contract :
                                    if not rec.excuse_check_in:
                                        if not  self.run_from_cron:

                                            if not self.check_multiple_entry_issue(rec.employee_id.id,'morning'):
                                                record = self.env['hr.work.entry'].sudo().create({
                                                    'contract_id': rec.sudo().employee_id.contract_id.id,
                                                    'name': "متأخر %s" % (rec.employee_id.name),
                                                    'date_start':start_date,
                                                    'date_stop': dt_in_utc ,
                                                    'employee_id': rec.employee_id.id,
                                                    'work_entry_type_id': work_entry_type.id,
                                                })
                                    
                        if schedule.day_period == 'afternoon' and rec.day_period == 'afternoon':
                            work_from = schedule.hour_from
                            result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_from * 60, 60))
                            user_tz = self.env.user.tz
                            dt_in_utc = rec.check_in
                            dt_out_utc = rec.check_out
                            #logging.info('dt_in_utc---ssssssssssss-------%s-----',dt_in_utc)
                            #logging.info('dt_out_utc----ssssssssssssssssss------%s-----',dt_out_utc)
                            if dt_out_utc== False:
                                continue
                            dt = rec.check_in
                            if user_tz in pytz.all_timezones:
                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                dt = old_tz.localize(dt).astimezone(new_tz)
                            str_time = dt.strftime("%H:%M")
                            check_in_date = datetime.strptime(str_time, "%H:%M").time()
                            start_date = datetime.strptime(result, "%H:%M").time()
                            t1 = timedelta(hours=check_in_date.hour, minutes=check_in_date.minute)
                            t2 = timedelta(hours=start_date.hour, minutes=start_date.minute)
                            if check_in_date > start_date:
                                final = t1 - t2
                                rec.sudo().late_check_in = final.total_seconds() / 60

                            if rec.late_check_in > 0:
                                rec.sudo().late_check_in = 0.0
                                
                                work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)  

                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                start_date = dt_in_utc.date()+relativedelta(hours=work_from, minutes=0, seconds=0)
                                if self.check_leave(start_date,rec.employee_id):
                                    continue
                                start_date =  fields.Datetime.to_string(new_tz.localize(start_date).astimezone(old_tz))
                                #logging.info('work_from----------%s-----',work_from)
                                #logging.info('today_date.date----------%s-----',start_date)
                                #logging.info('dt_in_utc----------%s-----',dt_in_utc)
                                #logging.info('dt_out_utc----------%s-----',dt_out_utc)
                                #if contact end date time of day must be greater than check in time
                                end_date_as_par_contract =  dt_in_utc.date()+relativedelta(hours=schedule.hour_to, minutes=0, seconds=0)
                                #logging.info('end_date_as_par_contractend_date_as_par_contract----------%s-----',end_date_as_par_contract)
                                if dt_in_utc < end_date_as_par_contract :
                                    if not rec.excuse_check_in:
                                        if not  self.run_from_cron:
                                            #logging.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++%s",self.check_multiple_entry_issue(rec.employee_id.id,'afternoon'))
                                            if not self.check_multiple_entry_issue(rec.employee_id.id,'afternoon'):

                                                record = self.env['hr.work.entry'].sudo().create({
                                                    'contract_id': rec.sudo().employee_id.contract_id.id,
                                                    'name': "متأخر %s" % (rec.employee_id.name),
                                                    'date_start':start_date,
                                                    'date_stop': dt_in_utc ,
                                                    'employee_id': rec.employee_id.id,
                                                    'work_entry_type_id': work_entry_type.id,
                                                })
                        if schedule.day_period == 'morning' and rec.day_period == 'morning':
                            work_to = schedule.hour_to
                            result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_to * 60, 60))

                            user_tz = self.env.user.tz
                            dt_in_utc = rec.check_in
                            dt_out_utc = rec.check_out
                            dt = rec.check_in
                            dt_out = rec.check_out
                            if user_tz in pytz.all_timezones:
                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                dt = old_tz.localize(dt).astimezone(new_tz)
                                dt_out = old_tz.localize(dt_out).astimezone(new_tz)

                            end_time = dt_out.strftime("%H:%M")
                            check_out_date = datetime.strptime(end_time, "%H:%M").time()
                            end_date = datetime.strptime(result, "%H:%M").time()
                            t1 = timedelta(hours=check_out_date.hour, minutes=check_out_date.minute)
                            t2 = timedelta(hours=end_date.hour, minutes=end_date.minute)
                            if check_out_date < end_date:
                                final = t2 - t1
                                rec.sudo().early_exit = final.total_seconds() / 60
                            #logging.info("check_out_date-------------%s--------",check_out_date)
                            #logging.info("end_date-------------%s--------",end_date)
                            if rec.early_exit > 0:
                                rec.sudo().early_exit = 0.0
                                end_display_date = dt_in_utc.date()+relativedelta(hours=work_to, minutes=0, seconds=0)
                                if self.check_leave(end_display_date,rec.employee_id):
                                    continue
                                end_display_date =  fields.Datetime.to_string(new_tz.localize(end_display_date).astimezone(old_tz))
                                if not rec.excuse_check_out:
                                    work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)
                                    if not  self.run_from_cron:
                                            if not self.check_multiple_entry_issue(rec.employee_id.id,'morning'):

                                                record = self.env['hr.work.entry'].sudo().create({
                                                    'contract_id': rec.sudo().employee_id.contract_id.id,
                                                    'name': "خروج مبكر %s" % (rec.employee_id.name),
                                                    'date_start': dt_out_utc,
                                                    'date_stop': end_display_date,
                                                    'employee_id': rec.employee_id.id,
                                                    'work_entry_type_id': work_entry_type.id,
                                                })
                        #logging.info("schedule.day_period-------------%s--------",schedule.day_period)
                        #logging.info("srec.day_period-------------%s--------",rec.day_period)
                        if schedule.day_period == 'afternoon' and rec.day_period == 'afternoon':
                            work_to = schedule.hour_to
                            result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_to * 60, 60))
                            user_tz = self.env.user.tz
                            dt_in_utc = rec.check_in
                            dt_out_utc = rec.check_out
                            dt = rec.check_in
                            dt_out = rec.check_out
                            if user_tz in pytz.all_timezones:
                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                dt = old_tz.localize(dt).astimezone(new_tz)
                                dt_out = old_tz.localize(dt_out).astimezone(new_tz)

                            end_time = dt_out.strftime("%H:%M")
                            check_out_date = datetime.strptime(end_time, "%H:%M").time()
                            end_date = datetime.strptime(result, "%H:%M").time()
                            t1 = timedelta(hours=check_out_date.hour, minutes=check_out_date.minute)
                            t2 = timedelta(hours=end_date.hour, minutes=end_date.minute)
                            #logging.info("check_out_date-------------%s--------",dt_out_utc)
                            #logging.info("end_date-------------%s--------",check_out_date)

                            if check_out_date < end_date:
                                final = t2 - t1
                                rec.sudo().early_exit = final.total_seconds() / 60

                            if rec.early_exit > 0:
                                rec.sudo().early_exit = 0.0
                                end_display_date = dt_in_utc.date()+relativedelta(hours=work_to, minutes=0, seconds=0)
                                if self.check_leave(end_display_date,rec.employee_id):
                                    continue
                                end_display_date =  fields.Datetime.to_string(new_tz.localize(end_display_date).astimezone(old_tz))
                                if not rec.excuse_check_out:
                                    work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)
                                    if not  self.run_from_cron:
                                            if not self.check_multiple_entry_issue(rec.employee_id.id,'afternoon'):

                                                record = self.env['hr.work.entry'].sudo().create({
                                                    'contract_id': rec.sudo().employee_id.contract_id.id,
                                                    'name': "خروج مبكر %s" % (rec.employee_id.name),
                                                    'date_start': dt_out_utc,
                                                    'date_stop': end_display_date,
                                                    'employee_id': rec.employee_id.id,
                                                    'work_entry_type_id': work_entry_type.id,
                                                })
    def create_entry_work_tripday(self,new_date_from,new_date_to,employee_id):
        new_date_to=datetime.strptime((new_date_to).strftime('%Y-%m-%d %H:%M:%S'), DEFAULT_SERVER_DATETIME_FORMAT)

        att_recs = self.env['hr.attendance'].sudo().search([('check_in', '>=', new_date_from),('is_trip_entry','=',True),
                                    ('check_out', '<=', new_date_to),
                                    ('employee_id', '=', employee_id.id)])
        #logging.info("lisnew_date_from----------------------%s",new_date_from)
        #logging.info("new_date_to----------------------%s",new_date_to)
        #logging.info("employee_id.id----------------------%s",employee_id.id)
        #logging.info("employee_id.att_recs----------------------%s",att_recs)
        #logging.info("att_recs---------------------------%s",att_recs)

        if len(att_recs):

            att_recs_normal_entries = self.env['hr.attendance'].sudo().search([('check_in', '>=', new_date_from),('is_trip_entry','=',False),
                                        ('check_out', '<=', new_date_to),
                                        ('employee_id', '=', employee_id.id)])
            
            list_period=[]
            for normal_rec in att_recs_normal_entries:

                list_period.append(normal_rec.day_period)
            #logging.info("list per---------------------------%s",list_period)
            work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)

            if 'morning' not in list_period:
                if not  self.run_from_cron:
                    # not_absent=False
                    # for rec in att_recs:
                    #     if rec.day_period=='morning':
                    #         not_absent=True
                    #         #logging.info("Not create entry$$$$$$$$$$$$$$$$$$$$$$$$######################")
                    # if not not_absent:
                        date_dic=self.env['late.regeneration.wizard'].get_date_start_stop(employee_id,new_date_from,"morning")
                        if date_dic['holiday']==False:
                                self.env['hr.work.entry'].sudo().create({
                                    'contract_id': employee_id.contract_id.id,
                                    'name': "غائب: %s" % (employee_id.name),
                                    'date_start': date_dic['start_date'],
                                    'date_stop':date_dic['end_date'],
                                    'employee_id': employee_id.id,
                                    'work_entry_type_id': work_entry_type.id,
                                })
            if 'afternoon' not in list_period:
                    if not  self.run_from_cron:

                        date_dic=self.env['late.regeneration.wizard'].get_date_start_stop(employee_id,new_date_from,"afternoon")
                        if date_dic['holiday']==False:

                            self.env['hr.work.entry'].sudo().create({
                                'contract_id': employee_id.contract_id.id,
                                'name': "غائب: %s" % (employee_id.name),
                                'date_start': date_dic['start_date'],
                                'date_stop':date_dic['end_date'],
                                'employee_id': employee_id.id,
                                'work_entry_type_id': work_entry_type.id,
                            })

 



        return
                          

    def absent_employee(self):
        records = self.env['hr.attendance'].sudo().search([('check_in', '<=', datetime.now()),('is_trip_entry','=',False),
                                                    ('check_in', '>=', datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))])
        #logging.info("today weekkkkkkkkkkkkkkk%s------------", datetime.now())
        #logging.info("today weekkkkkkkkkkkkkkk%s------------",datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))
        employees = self.env['hr.employee'].sudo().search([])
        emp_present_list = []
        x = date.today()
        today_week_day =date.today().weekday()
        old_tz = pytz.timezone('UTC')
        new_tz = pytz.timezone(self.env.user.tz)
   
        for rec in records:
            if rec.sudo().employee_id.contract_id:
                emp_present_list.append(rec.employee_id.id)
##################################for 1 absenty##########################################
        for emp in employees:
            if emp.sudo().contract_id and emp.sudo().contract_id.state == 'open' and emp.sudo().contract_id.flexible == False:
                if emp.id  in emp_present_list:
                    emp_records = self.env['hr.attendance'].sudo().search([('employee_id','=',emp.id),('check_in', '<=', datetime.now()),('is_trip_entry','=',False),
                                                    ('check_in', '>=', datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))])

                    if len(emp_records) >1:
                        self.create_entry_work_tripday(datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'),datetime.now(),emp)

                    if len(emp_records) == 1:
                        if emp_records.day_period=='morning':
                    
                            for attendance_day_data in emp.resource_calendar_id.attendance_ids:
                                # #logging.info("today weekkkkkkkkkkkkkkk%s------------",today_week_day)
                                #logging.info("today attendance_day_data.dayofweek%s",attendance_day_data.dayofweek)
                                #logging.info("today attendance_day_data.dayofweek%s",today_week_day)
                                if attendance_day_data.day_period == 'afternoon':
                                    if attendance_day_data.dayofweek  == str(today_week_day):
                                            work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)
                                            start_date = x+relativedelta(hours=attendance_day_data.hour_from, minutes=0, seconds=0)
                                            start_date_not_str= new_tz.localize(start_date).astimezone(old_tz)
                                            if self.check_leave(start_date,emp):
                                                continue
                                            start_date =  fields.Datetime.to_string(new_tz.localize(start_date).astimezone(old_tz))
                                        
                                            end_date = x+relativedelta(hours=attendance_day_data.hour_to, minutes=0, seconds=0)
                                            end_date_not_str= new_tz.localize(end_date).astimezone(old_tz)

                                            end_date = fields.Datetime.to_string(new_tz.localize(end_date).astimezone(old_tz))
                                            if not  self.run_from_cron:
                                                #logging.info("emp_records.check_out----------------%s",emp_records.check_out)
                                                #logging.info("emp_records.check_out----------------%s",start_date_not_str.replace(tzinfo=None))

                                                if emp_records.check_out<=start_date_not_str.replace(tzinfo=None):
    

                                                    mrn_record = self.env['hr.work.entry'].sudo().create({
                                                        'contract_id': emp.sudo().contract_id.id,
                                                        'name': "غائب: %s" % (emp.name),
                                                        'date_start': start_date,
                                                        'date_stop': end_date,
                                                        'employee_id': emp.id,
                                                        'work_entry_type_id': work_entry_type.id,
                                                    })
                                                else:
                                                        if emp_records.check_out<end_date_not_str.replace(tzinfo=None):

                                                            mrn_record = self.env['hr.work.entry'].sudo().create({
                                                        'contract_id': emp.sudo().contract_id.id,
                                                        'name': "Early: %s" % (emp.name),
                                                        'date_start':emp_records.check_out ,
                                                        'date_stop': end_date,
                                                        'employee_id': emp.id,
                                                        'work_entry_type_id': work_entry_type.id,
                                                    })


                        else:
                            for attendance_day_data in emp.resource_calendar_id.attendance_ids:
                                # #logging.info("today weekkkkkkkkkkkkkkk%s------------",today_week_day)
                                #logging.info("today attendance_day_data.dayofweek%s",attendance_day_data.dayofweek)
                                #logging.info("today attendance_day_data.dayofweek%s",today_week_day)
                                if attendance_day_data.day_period == 'morning':
                                    if attendance_day_data.dayofweek  == str(today_week_day):
                                            work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)
                                            start_date = x+relativedelta(hours=attendance_day_data.hour_from, minutes=0, seconds=0)
                                            start_date_not_str = x+relativedelta(hours=attendance_day_data.hour_from, minutes=0, seconds=0)

                                            if self.check_leave(start_date,emp):
                                                continue
                                            start_date =  fields.Datetime.to_string(new_tz.localize(start_date).astimezone(old_tz))
                                        
                                            end_date = x+relativedelta(hours=attendance_day_data.hour_to, minutes=0, seconds=0)
                                            end_date = fields.Datetime.to_string(new_tz.localize(end_date).astimezone(old_tz))
                                            if not  self.run_from_cron:

                                                    mrn_record = self.env['hr.work.entry'].sudo().create({
                                                        'contract_id': emp.sudo().contract_id.id,
                                                        'name': "غائب: %s" % (emp.name),
                                                        'date_start': start_date,
                                                        'date_stop': end_date,
                                                        'employee_id': emp.id,
                                                        'work_entry_type_id': work_entry_type.id,
                                                    })
                    

########################################################################################
                

        for emp in employees:
            if emp.sudo().contract_id and emp.sudo().contract_id.state == 'open' and emp.sudo().contract_id.flexible == False:
                if emp.id not in emp_present_list:
                    
                    for attendance_day_data in emp.resource_calendar_id.attendance_ids:
                        # #logging.info("today weekkkkkkkkkkkkkkk%s------------",today_week_day)
                        #logging.info("today attendance_day_data.dayofweek%s",attendance_day_data.dayofweek)
                        #logging.info("today attendance_day_data.dayofweek%s",today_week_day)

                        if attendance_day_data.dayofweek  == str(today_week_day):
                                work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)
                                start_date = x+relativedelta(hours=attendance_day_data.hour_from, minutes=0, seconds=0)
                                if self.check_leave(start_date,emp):
                                    continue
                                start_date =  fields.Datetime.to_string(new_tz.localize(start_date).astimezone(old_tz))
                               
                                end_date = x+relativedelta(hours=attendance_day_data.hour_to, minutes=0, seconds=0)
                                end_date = fields.Datetime.to_string(new_tz.localize(end_date).astimezone(old_tz))
                                if not  self.run_from_cron:

                                    mrn_record = self.env['hr.work.entry'].sudo().create({
                                        'contract_id': emp.sudo().contract_id.id,
                                        'name': "غائب: %s" % (emp.name),
                                        'date_start': start_date,
                                        'date_stop': end_date,
                                        'employee_id': emp.id,
                                        'work_entry_type_id': work_entry_type.id,
                                    })



                          


class LateRegenerationWizard(models.TransientModel):
    _name = 'late.regeneration.wizard'
    _description = 'Regenerate Employee Late'

    earliest_available_date = fields.Date('Earliest date', compute='_compute_earliest_available_date')
    earliest_available_date_message = fields.Char(readonly=True, store=False, default='')
    latest_available_date = fields.Date('Latest date', compute='_compute_latest_available_date')
    latest_available_date_message = fields.Char(readonly=True, store=False, default='')
    date_from = fields.Date('From', required=True, default=lambda self: self.env.context.get('date_start'))
    date_to = fields.Date('To', required=True, default=lambda self: self.env.context.get('date_end'))
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    validated_work_entry_ids = fields.Many2many('hr.work.entry', string='Work Entries Within Interval',
                                   compute='_compute_validated_work_entry_ids')
    search_criteria_completed = fields.Boolean(compute='_compute_search_criteria_completed')
    valid = fields.Boolean(compute='_compute_valid')

    @api.depends('employee_id')
    def _compute_earliest_available_date(self):
        for wizard in self:
            dates = wizard.mapped('employee_id.contract_ids.date_generated_from')
            wizard.earliest_available_date = min(dates) if dates else None

    @api.depends('employee_id')
    def _compute_latest_available_date(self):
        for wizard in self:
            dates = wizard.mapped('employee_id.contract_ids.date_generated_to')
            wizard.latest_available_date = max(dates) if dates else None

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_validated_work_entry_ids(self):
        for wizard in self:
            validated_work_entry_ids = self.env['hr.work.entry']
            if wizard.search_criteria_completed:
                search_domain = [('employee_id', '=', self.employee_id.id),
                                 ('date_start', '>=', self.date_from),
                                 ('date_stop', '<=', self.date_to),
                                 ('state', '=', 'validated')]
                validated_work_entry_ids = self.env['hr.work.entry'].sudo().search(search_domain, order="date_start")
            wizard.validated_work_entry_ids = validated_work_entry_ids

    @api.depends('validated_work_entry_ids')
    def _compute_valid(self):
        for wizard in self:
            wizard.valid = wizard.search_criteria_completed and len(wizard.validated_work_entry_ids) == 0

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_search_criteria_completed(self):
        for wizard in self:
            wizard.search_criteria_completed = self.date_from and self.date_to and self.employee_id

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _check_dates(self):
        for wizard in self:
            wizard.earliest_available_date_message = ''
            wizard.latest_available_date_message = ''
            if wizard.search_criteria_completed:
                if wizard.date_from > wizard.date_to:
                    date_from = wizard.date_from
                    wizard.date_from = wizard.date_to
                    wizard.date_to = date_from
                if wizard.earliest_available_date and wizard.date_from < wizard.earliest_available_date:
                    wizard.date_from = wizard.earliest_available_date
                    wizard.earliest_available_date_message = _('The earliest available date is %s', self._date_to_string(wizard.earliest_available_date))
                if wizard.latest_available_date and wizard.date_to > wizard.latest_available_date:
                    wizard.date_to = wizard.latest_available_date
                    wizard.latest_available_date_message = _('The latest available date is %s', self._date_to_string(wizard.latest_available_date))

    @api.model
    def _date_to_string(self, date):
        if not date:
            return ''
        user_date_format = self.env['res.lang']._lang_get(self.env.user.lang).date_format
        return date.strftime(user_date_format)


    def check_leave_detail(self,date_today,emp):
        leave_obj=self.env['hr.leave']
        dic={}
        lst=[]
        #logging.info("date_today%s__??????????????????????????????????",date_today)

        att_recs = leave_obj.search([('request_date_from', '<=', date_today),
                                    ('request_date_to', '>=', date_today),
                                    ('employee_id', '=', emp.id),('state','=','validate')])

        if len(att_recs) : 

            for rec in att_recs:
                if rec.request_unit_half:
                    dic['leave_type']='half_day'
                    dic['leave_period']=rec.request_date_from_period
                    dic['leave_entry_type']=rec.holiday_status_id.work_entry_type_id
                    
                elif rec.request_unit_hours:
                    dic['leave_type']='custom_hours'
                    dic['leave_hour_from']=rec.request_hour_from
                    dic['leave_hour_to']=rec.request_hour_to
                    dic['leave_entry_type']=rec.holiday_status_id.work_entry_type_id


                else:
                    dic['leave_type']='full_days'                  
                    dic['leave_entry_type']=rec.holiday_status_id.work_entry_type_id
                lst.append(dic)
                dic={}
            return lst
        else:
            dic['leave_type']='no_leave'
            return lst.append(dic)
        
    def check_leave(self,date_today,emp,day_period):
        leave_obj=self.env['hr.leave']
        if day_period=='morning':
            period='am'
        else:
            period='pm'
        #logging.info("date_today%s__??????????????????????????????????",date_today)
        if type(emp) == int:
              att_recs = leave_obj.search([('request_date_from', '<=', date_today),
                                    ('request_date_to', '>=', date_today),
                                    ('employee_id', '=', emp.id),('state','=','validate'),('request_unit_hours','=',False)])

        else:
       
             att_recs = leave_obj.search([('request_date_from', '<=', date_today),
                                    ('request_date_to', '>=', date_today),
                                    ('employee_id', '=', emp.id),('state','=','validate'),('request_unit_hours','=',False)])

        if len(att_recs) : 
            for rec in att_recs:
                if rec.request_unit_half:
                    if rec.request_date_from_period == 'am' and day_period == 'morning':
                        return True
                
                    if rec.request_date_from_period == 'pm' and day_period == 'afternoon':
                        return True
                    return False
            return True    
                                    
                        
        else:
            return False
            
   
    

    def get_date_start_stop(self,emp,date_today,day_period):
        date_dic = {}
        x = date.today()
        today_week_day =date_today.weekday()
        old_tz = pytz.timezone('UTC')
        new_tz = pytz.timezone(self.env.user.tz)
   
        emps=self.env['hr.employee'].browse(emp)

        if emp.contract_id and emp.contract_id.state == 'open' and emp.contract_id.flexible == False:

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
                    # else:
                    #     date_dic['holiday']=True


            # date_dic['holiday']=True
        if self.check_leave(date_today,emps.id,day_period):
                date_dic['holiday']=True
                return date_dic

        if not date_dic.get("start_date",False):
                date_dic['holiday']=True


        return date_dic
                      
    def create_entry_work_tripday(self,new_date_from,new_date_to,employee_id):

        att_recs = self.env['hr.attendance'].sudo().search([('check_in', '>', new_date_from),('is_trip_entry','=',True),
                                    ('check_out', '<', new_date_to),
                                    ('employee_id', '=', employee_id.id)])
        if len(att_recs):

            att_recs_normal_entries = self.env['hr.attendance'].sudo().search([('check_in', '>', new_date_from),('is_trip_entry','=',False),
                                        ('check_out', '<', new_date_to),
                                        ('employee_id', '=', employee_id.id)])
            
            list_period=[]
            for normal_rec in att_recs_normal_entries:
                
                list_period.append(normal_rec.day_period)
            #logging.info("list per---------------------------%s",list_period)
            work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)

            if 'morning' not in list_period:
                   date_dic=self.get_date_start_stop(employee_id,new_date_from,"morning")
                   if date_dic['holiday']==False:
                        self.env['hr.work.entry'].sudo().create({
                            'contract_id': employee_id.contract_id.id,
                            'name': "غائب: %s" % (employee_id.name),
                            'date_start': date_dic['start_date'],
                            'date_stop':date_dic['end_date'],
                            'employee_id': employee_id.id,
                            'work_entry_type_id': work_entry_type.id,
                        })
            if 'afternoon' not in list_period:
                        noon=False
                        ndate_dic=self.get_date_start_stop(employee_id,new_date_from,"afternoon")

                        for normal_rec in att_recs:
                            logging.info("normal_rec.check_out====================================%s",normal_rec.check_out)
                            logging.info("normal_rec.ndate_dic['start_date_not_str']====================================%s",ndate_dic['start_date_not_str'])

                            if normal_rec.check_out >=ndate_dic['start_date_not_str']:
                                noon=True
                        if not noon:
                            date_dic=self.get_date_start_stop(employee_id,new_date_from,"afternoon")
                            if date_dic['holiday']==False:

                                self.env['hr.work.entry'].sudo().create({
                                    'contract_id': employee_id.contract_id.id,
                                    'name': "غائب: %s" % (employee_id.name),
                                    'date_start': date_dic['start_date'],
                                    'date_stop':date_dic['end_date'],
                                    'employee_id': employee_id.id,
                                    'work_entry_type_id': work_entry_type.id,
                                })

 



        return
        
    def check_multiple_entry_issue_wizard(self,employee_id,day_period,date_from,date_to):
      
        data= self.env['hr.attendance'].sudo().search([('employee_id','=',employee_id),('day_period_m','=',day_period),('is_trip_entry','=',False),('check_out', '<', date_to),('is_trip_entry','=',False),
                                            ('check_in', '>=',date_from)], order='id asc')
        # ##logging.info('*********************************************date_to********-%s-----',date_to)

        # ##logging.info('*********************************************date_from********-%s-----',date_from)
        # ##logging.info('*********************************************data********-%s-----',data)

        if len(data)>1:
                return True
        else:
            return False
    def check_multiple_entry_issue_no_wizard(self,employee_id,day_period,date_from,date_to):
        previous_date=False
        previous_date_early=False
        previous_date_morning=False
        early_check_in=False
        worked_more_then_break_in_morning=False
        created_entry_list=[]

      
        data= self.env['hr.attendance'].sudo().search([('employee_id','=',employee_id),('day_period_m','=',day_period),('is_trip_entry','=',False),('excuse_check_in','=',False),('excuse_check_out','=',False),('check_out', '<', date_to),('is_trip_entry','=',False),
                                            ('check_in', '>=',date_from)], order='id asc')


        if day_period == 'afternoon':

            data_morning= self.env['hr.attendance'].sudo().search([('employee_id','=',employee_id),('day_period_m','=','morning'),('is_trip_entry','=',False),('excuse_check_in','=',False),('excuse_check_out','=',False),('check_out', '<', date_to),('is_trip_entry','=',False),
                                                ('check_in', '>=',date_from)], order='id asc')

            if len(data_morning)==1:
                    emp_browse_data=self.env['hr.employee'].browse(employee_id)

                    date_dic_morning=self.get_date_start_stop(emp_browse_data,date_from,"morning")
                    
                    if date_dic_morning.get('end_date_not_str',False):
                        if date_dic_morning['end_date_not_str'] < data_morning[0].check_out+relativedelta(hours=1, minutes=0, seconds=0):
                            previous_date=data_morning[0].check_out
      
      
      
        logging.info('************************************previous_date*********date_to********-%s-----',previous_date)

        # ##logging.info('*********************************************date_from********-%s-----',date_from)

        if len(data)>1:
            no_break=False

            for att in data:
                if att.no_break:
                    no_break=True
          
            small_id_noon=0
            if len(data):
                no_break=False

                for atts in data:
                    if atts.no_break:
                    #  check_out=atts.check_out
                        no_break=True
                if no_break:
                    aft_list=[]
                    for atts in data:
                        if atts.day_period=='afternoon':
                            if atts.no_break==False:

                                aft_list.append(atts.id)
                            small_id_noon=aft_list[:1]
                            ##logging.info("small_id_noon----------------------------------------------%s__----------------",small_id_noon)


                          
        
            rec =data[-1]
            rec.late_check_in = 0.0
            rec.early_exit = 0.0
            week_day = rec.sudo().check_in.weekday()
            work_schedule = rec.sudo().employee_id.resource_calendar_id
            early_check_in =False

            for schedule in work_schedule.sudo().attendance_ids:
                #logging.info('*****************************************************-%s-----',rec.day_period)

                if schedule.dayofweek == str(week_day):
                    if schedule.day_period == 'morning' and rec.day_period == 'morning':
                            emp_browse_data=self.env['hr.employee'].browse(employee_id)
                            date_dic=self.get_date_start_stop(emp_browse_data,date_from,"morning")
                            if rec.check_in < date_dic['start_date_not_str']:
                                early_check_in =True
                            work_to = schedule.hour_to
                            result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_to * 60, 60))

                            user_tz = self.env.user.tz
                            dt_in_utc = rec.check_in
                            dt_out_utc = rec.check_out
                            dt = rec.check_in
                            dt_out = rec.check_out
                            if user_tz in pytz.all_timezones:
                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                dt = old_tz.localize(dt).astimezone(new_tz)
                                dt_out = old_tz.localize(dt_out).astimezone(new_tz)

                            end_time = dt_out.strftime("%H:%M")
                            check_out_date = datetime.strptime(end_time, "%H:%M").time()
                            end_date = datetime.strptime(result, "%H:%M").time()
                            t1 = timedelta(hours=check_out_date.hour, minutes=check_out_date.minute)
                            t2 = timedelta(hours=end_date.hour, minutes=end_date.minute)
                            if check_out_date < end_date:
                                final = t2 - t1
                                rec.sudo().early_exit = final.total_seconds() / 60
                            #logging.info("check_out_date-------------%s--------",check_out_date)
                            #logging.info("end_date-------------%s--------",end_date)
                            if rec.early_exit > 0:
                                rec.sudo().early_exit = 0.0
                                end_display_date = dt_in_utc.date()+relativedelta(hours=work_to, minutes=0, seconds=0)
                                if self.check_leave(end_display_date,rec.employee_id,'morning'):
                                    continue
                                end_display_date =  fields.Datetime.to_string(new_tz.localize(end_display_date).astimezone(old_tz))
                                if not rec.excuse_check_out:
                                    
                                    work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)
                                    record = self.env['hr.work.entry'].sudo().create({
                                                        'contract_id': rec.sudo().employee_id.contract_id.id,
                                                        'name': "خروج مبكر %s" % (rec.employee_id.name),
                                                        'date_start': dt_out_utc,
                                                        'date_stop': end_display_date,
                                                        'employee_id': rec.employee_id.id,
                                                        'work_entry_type_id': work_entry_type.id,
                                                    })
                                    created_entry_list.append(record)

                    if schedule.day_period == 'afternoon' and rec.day_period == 'afternoon':
                        work_to = schedule.hour_to
                        result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_to * 60, 60))
                        user_tz = self.env.user.tz
                        dt_in_utc = rec.check_in
                        dt_out_utc = rec.check_out
                        dt = rec.check_in
                        dt_out = rec.check_out
                        if user_tz in pytz.all_timezones:
                            old_tz = pytz.timezone('UTC')
                            new_tz = pytz.timezone(user_tz)
                            dt = old_tz.localize(dt).astimezone(new_tz)
                            dt_out = old_tz.localize(dt_out).astimezone(new_tz)

                        end_time = dt_out.strftime("%H:%M")
                        check_out_date = datetime.strptime(end_time, "%H:%M").time()
                        end_date = datetime.strptime(result, "%H:%M").time()
                        t1 = timedelta(hours=check_out_date.hour, minutes=check_out_date.minute)
                        t2 = timedelta(hours=end_date.hour, minutes=end_date.minute)
                        #logging.info("check_out_date-------------%s--------",dt_out_utc)
                        #logging.info("end_date-------------%s--------",check_out_date)

                        if check_out_date < end_date:
                            final = t2 - t1
                            rec.sudo().early_exit = final.total_seconds() / 60

                        if rec.early_exit > 0:
                            rec.sudo().early_exit = 0.0
                            end_display_date = dt_in_utc.date()+relativedelta(hours=work_to, minutes=0, seconds=0)
                            if self.check_leave(end_display_date,rec.employee_id,'afternoon'):
                                continue
                            end_display_date =  fields.Datetime.to_string(new_tz.localize(end_display_date).astimezone(old_tz))
                            if not rec.excuse_check_out:
                                work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)
                                if previous_date_early!=False:
                                    start_date=previous_date_early
                                if not rec.no_break:
                                    record = self.env['hr.work.entry'].sudo().create({
                                        'contract_id': rec.sudo().employee_id.contract_id.id,
                                        'name': "خروج مبكر %s" % (rec.employee_id.name),
                                        'date_start': dt_out_utc,
                                        'date_stop': end_display_date,
                                        'employee_id': rec.employee_id.id,
                                        'work_entry_type_id': work_entry_type.id,
                                    })
                                    created_entry_list.append(record)

                 
 
            for rec in data:
                ##logging.info('**************************data***************************-%s-----',data)

                rec.late_check_in = 0.0
                rec.early_exit = 0.0
                early_check_in=False
                week_day = rec.sudo().check_in.weekday()
                work_schedule = rec.sudo().employee_id.resource_calendar_id
                for schedule in work_schedule.sudo().attendance_ids:
                    ##logging.info('*****************************************************-%s-----',rec.day_period)

                    if schedule.dayofweek == str(week_day):
                        if schedule.day_period == 'morning' and rec.day_period == 'morning':
                            work_from = schedule.hour_from
                            result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_from * 60, 60))

                            user_tz = self.env.user.tz
                            dt_in_utc = rec.check_in
                            dt_out_utc = rec.check_out
                            dt = rec.check_in
                            dt_out = rec.check_out
                            if user_tz in pytz.all_timezones:
                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                dt = old_tz.localize(dt).astimezone(new_tz)
                                #logging.info("rec-------------------------%s",rec.sudo().employee_id.contract_id)
                                #logging.info("rec-------------------------%s",rec)
                                #logging.info("date-------------------------%s",dt_out)
                                if not dt_out:
                                    continue
                                dt_out = old_tz.localize(dt_out).astimezone(new_tz)

                            str_time = dt.strftime("%H:%M")
                            check_in_date = datetime.strptime(str_time, "%H:%M").time()
                            start_date = datetime.strptime(result, "%H:%M").time()
                            t1 = timedelta(hours=check_in_date.hour, minutes=check_in_date.minute)
                            t2 = timedelta(hours=start_date.hour, minutes=start_date.minute)
                            # if check_in_date > start_date:
                            #     final = t1 - t2
                            #     rec.sudo().late_check_in = final.total_seconds() / 60
                            # ##logging.info('mmmm--------')

                            # # if rec.late_check_in > 0:
                            # if rec.late_check_in :
                   
                            ##logging.info('LLLLLLLLLLLLLL--------')

                            rec.sudo().late_check_in = 0.0
                            work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)  

                            old_tz = pytz.timezone('UTC')
                            new_tz = pytz.timezone(user_tz)
                            start_date = dt_in_utc.date()+relativedelta(hours=work_from, minutes=0, seconds=0)
                            if self.check_leave(start_date,rec.employee_id,'morning'):
                                continue
                            start_date =  fields.Datetime.to_string(new_tz.localize(start_date).astimezone(old_tz))
                            #logging.info('work_from----------%s-----',start_date)
                            #logging.info('today_date.date------*******************----%s-----',dt_in_utc.date())
                            #logging.info('dt_in_utc----------%s-----',dt_in_utc)
                            ##logging.info('previous_date_morning----------%s-----',previous_date_morning)
                            start_date_as_par_contract =  dt_in_utc.date()+relativedelta(hours=schedule.hour_from, minutes=0, seconds=0)

                            end_date_as_par_contract =  dt_in_utc.date()+relativedelta(hours=schedule.hour_to, minutes=0, seconds=0)
                            end_date_as_par_contract_display = fields.Datetime.to_string(new_tz.localize(end_date_as_par_contract).astimezone(old_tz))
                            ##logging.info('end_date_as_par_contractend_date_as_par_contract----------%s-----',end_date_as_par_contract)
                            start_date_as_par_contract_display = fields.Datetime.to_string(new_tz.localize(start_date_as_par_contract).astimezone(old_tz))
                            #logging.info('start_date_as_par_contract_display----------%s-----',start_date_as_par_contract_display)

                            if  dt_in_utc  < start_date_as_par_contract:
                                        early_check_in =True
                            if dt_in_utc < end_date_as_par_contract :
                                if not rec.excuse_check_in:
                                        if previous_date_morning!=False:
                                            start_date=previous_date_morning
                                        # if not early_check_in:
                                            
                                            record = self.env['hr.work.entry'].sudo().create({
                                                'contract_id': rec.sudo().employee_id.contract_id.id,
                                                'name': "غير متواجد: %s" % (rec.employee_id.name),
                                                'date_start':start_date,
                                                'date_stop': dt_in_utc ,
                                                'employee_id': rec.employee_id.id,
                                                'work_entry_type_id': work_entry_type.id,
                                            })
                                            created_entry_list.append(record)

                                        else:
                                            if start_date_as_par_contract < dt_in_utc:
                                                record = self.env['hr.work.entry'].sudo().create({
                                                    'contract_id': rec.sudo().employee_id.contract_id.id,
                                                    'name': "غير متواجد: %s" % (rec.employee_id.name),
                                                    'date_start':start_date_as_par_contract_display,
                                                    'date_stop': dt_in_utc ,
                                                    'employee_id': rec.employee_id.id,
                                                    'work_entry_type_id': work_entry_type.id,
                                                })
                                                created_entry_list.append(record)

                        previous_date_morning=dt_out_utc




                        if schedule.day_period == 'afternoon' and rec.day_period == 'afternoon':
                            work_from = schedule.hour_from
                            result = '{0:02.0f}:{1:02.0f}'.format(*divmod(work_from * 60, 60))
                            user_tz = self.env.user.tz
                            dt_in_utc = rec.check_in
                            dt_out_utc = rec.check_out
                            
                            ##logging.info('dt_in_utc---ssssssssssss-------%s-----',dt_in_utc)
                            ##logging.info('dt_out_utc----ssssssssssssssssss------%s-----',dt_out_utc)
                            if dt_out_utc== False:
                                continue
                            dt = rec.check_in
                            if user_tz in pytz.all_timezones:
                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                dt = old_tz.localize(dt).astimezone(new_tz)
                            str_time = dt.strftime("%H:%M")
                            check_in_date = datetime.strptime(str_time, "%H:%M").time()
                            start_date = datetime.strptime(result, "%H:%M").time()

                            t1 = timedelta(hours=check_in_date.hour, minutes=check_in_date.minute)
                            t2 = timedelta(hours=start_date.hour, minutes=start_date.minute)
                            if check_in_date > start_date:
                                final = t1 - t2
                                rec.sudo().late_check_in = final.total_seconds() / 60

                            if rec.late_check_in > 0:
                                rec.sudo().late_check_in = 0.0
                                
                                work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)  

                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(user_tz)
                                start_date = dt_in_utc.date()+relativedelta(hours=work_from, minutes=0, seconds=0)
                                if self.check_leave(start_date,rec.employee_id,'afternoon'):
                                    continue
                                # start_date =  fields.Datetime.to_string(new_tz.localize(start_date).astimezone(old_tz))
                                ##logging.info('work_from----------%s-----',work_from)
                                ##logging.info('today_date.date----------%s-----',start_date)
                                ##logging.info('dt_in_utc----------%s-----',dt_in_utc)
                                ##logging.info('dt_out_utc----------%s-----',dt_out_utc)
                                #if contact end date time of day must be greater than check in time
                                end_date_as_par_contract =  dt_in_utc.date()+relativedelta(hours=schedule.hour_to, minutes=0, seconds=0)
                                ##logging.info('end_date_as_par_contractend_date_as_par_contract----------%s-----',end_date_as_par_contract)
                                if dt_in_utc < end_date_as_par_contract :
                                    if not rec.excuse_check_in:
                                                if previous_date!=False:
                                                    start_date=previous_date
                                                if not no_break:
                                                    if dt_in_utc > start_date: 
                                                        record = self.env['hr.work.entry'].sudo().create({
                                                            'contract_id': rec.sudo().employee_id.contract_id.id,
                                                            'name': "غير متواجد: %s" % (rec.employee_id.name),
                                                            'date_start':start_date,
                                                            'date_stop': dt_in_utc ,
                                                            'employee_id': rec.employee_id.id,
                                                            'work_entry_type_id': work_entry_type.id,
                                                        })
                                                        logging.info('record-----dt_in_utc-----%s-----',dt_in_utc)

                                                        created_entry_list.append(record)


                                                if  small_id_noon!=0:
                                                        emp_browse_data=self.env['hr.employee'].browse(employee_id)

                                                        date_dic=self.get_date_start_stop(emp_browse_data,date_from,"afternoon")
                                                        if start_date <=date_dic['start_date_not_str']:
                                                            n=date_dic['start_date_not_str']
                                                        else:
                                                            n=start_date
                                                        record = self.env['hr.work.entry'].sudo().create({
                                                            'contract_id': rec.employee_id.contract_id.id,
                                                            'name': "متأخر %s" % (rec.employee_id.name),
                                                            'date_start':date_dic['start_date_not_str'],
                                                            'date_stop': dt_in_utc ,
                                                            'employee_id': rec.employee_id.id,
                                                            'work_entry_type_id': work_entry_type.id,
                                                        })
                                                        created_entry_list.append(record)


                            previous_date=dt_out_utc
            employee_id=self.env['hr.employee'].browse(employee_id)         
            # self.manage_conflict_entries(employee_id.contract_id,employee_id,created_entry_list,date_from)
            # self.make_attendance(employee_id.contract_id,employee_id,created_entry_list,date_from)

        return created_entry_list


    def  found_unwanted_overtime(self,date_today,employee_id,all_recs):
        date_dic = {}
        x = date.today()
        today_week_day =date_today.weekday()
        old_tz = pytz.timezone('UTC')
        new_tz = pytz.timezone(self.env.user.tz)
        new_list=[]
        emp=self.env['hr.employee'].browse(employee_id)
     

        if emp.contract_id and emp.contract_id.state == 'open' and emp.contract_id.flexible == False:

          for rec in all_recs:  
            for attendance_day_data in emp.resource_calendar_id.attendance_ids:
                  

                    if attendance_day_data.dayofweek  == str(today_week_day):
                        if attendance_day_data.day_period==rec.day_period:
                            start_date = date_today+relativedelta(hours=attendance_day_data.hour_from, minutes=0, seconds=0)
                            date_dic['start_date_not_str']=datetime.strptime(new_tz.localize(start_date).astimezone(old_tz).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')

                            start_date =  fields.Datetime.to_string(new_tz.localize(start_date).astimezone(old_tz))
                            date_dic['start_date']=start_date
                            
                            end_date = date_today+relativedelta(hours=attendance_day_data.hour_to, minutes=0, seconds=0)
                            date_dic['end_date_not_str']=datetime.strptime(new_tz.localize(end_date).astimezone(old_tz).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')
                            logging.info("removed externallllllllllllllllllllllllllllllllll%s",rec.check_in)
                            logging.info("removed externalllllllllllllllllllllend_datelllllllllllll%s",date_dic['end_date_not_str'])

                            if rec.check_in >=date_dic['end_date_not_str'] :

                                logging.info("removed externallllllllllllllllllllllllllllllllll%s",all_recs)

                                list(all_recs).remove(rec)
                                logging.info("removed externallllllllllllllllllllllllllllllllll%s",all_recs)
                            else:
                                new_list.append(rec.id)
                            end_date = fields.Datetime.to_string(new_tz.localize(end_date).astimezone(old_tz))
                            date_dic['end_date']=end_date




        return new_list
    
    
    def get_all_records_wiard(self):
        date_from=self.date_from
        date_to=self.date_to+relativedelta(hours=24, minutes=0, seconds=0)
        self.get_all_records(date_from,date_to,self.employee_id)

        return {
    'type': 'ir.actions.client',
    'tag': 'reload',
        }
    
    def get_all_records_cron(self):
        contract_running=self.env['hr.contract'].sudo().search([('state','=','open'),('flexible','=',False)])
        for contract in contract_running:
            self.get_all_records(False,False,contract.employee_id)
        return True

        
    def get_all_records(self,date_from,date_to,employee_id):
        if date_to == False:
            date_to_cron = datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            date_from_cron = datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') + relativedelta(hours=24, minutes=0, seconds=0)
            old_work_entry = self.env['hr.work.entry'].sudo().search([
                ('date_start', '>=', date_to_cron),
                ('date_stop', '<=', date_from_cron),
                ('employee_id', '=', employee_id.id)])
            old_work_entry.write({'active': False})
        else:
            old_work_date_to = date_to - relativedelta(days=1)
            old_work_entry = self.env['hr.work.entry'].sudo().search([
                ('date_start', '<=', old_work_date_to),
                ('date_stop', '>=', date_from),
                ('employee_id', '=', employee_id.id)])
            old_work_entry.write({'active': False})
        # employee_id=self.employee_id.id
        # employee_id=self.env['hr.employee'].browse(self.employee_id.id)
        entries_two = False
        entries_one = False
        attendance_obj=self.env['hr.attendance']
        contract_running=self.env['hr.contract'].search([('state','=','open'),('employee_id','=',employee_id.id),('flexible','=',False)])
        worked_more_then_break_in_morning=False
        cnt=0
        cnt_m=0
        next_count_m=1

        next_count=1
        if date_from!=False:

            total_days_count=(date_to-date_from).days
            total_days_count_m=(date_to-date_from).days

        if date_from==False:
             date_from=datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
             logging.info("new_date_from%s__----------------",date_from)
             date_to=datetime.strptime(date.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
             logging.info("date_to%s__----------------",date_to)

             total_days_count_m=1
             total_days_count=1
        while(cnt_m<total_days_count_m):
             new_date_to=datetime.strptime((date_from+timedelta(days=next_count_m)).strftime('%Y-%m-%d %H:%M:%S'), DEFAULT_SERVER_DATETIME_FORMAT)
             new_date_from=datetime.strptime((date_from+timedelta(days=cnt_m)).strftime('%Y-%m-%d %H:%M:%S'), DEFAULT_SERVER_DATETIME_FORMAT)
             logging.info("new_date_from%s__----------------",new_date_from)
             logging.info("da(((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((%s__----------------",date_from)
             for contract in contract_running:
                entries_one=self.check_multiple_entry_issue_no_wizard(contract.employee_id.id,'morning',new_date_from,new_date_to)
                entries_two=self.check_multiple_entry_issue_no_wizard(contract.employee_id.id,'afternoon',new_date_from,new_date_to)  
             cnt_m+=1
             next_count_m+=1


        # while(cnt<=total_days_count):
             early_check_in =False
             created_entry_list=[]

             new_date_to=datetime.strptime((date_from+timedelta(days=next_count)).strftime('%Y-%m-%d %H:%M:%S'), DEFAULT_SERVER_DATETIME_FORMAT)
             new_date_from=datetime.strptime((date_from+timedelta(days=cnt)).strftime('%Y-%m-%d %H:%M:%S'), DEFAULT_SERVER_DATETIME_FORMAT)
                      

             att_recs = self.env['hr.attendance'].sudo().search([('check_in', '>', new_date_from),('is_trip_entry','=',False),
                                            ('check_out', '<', new_date_to),
                                            ('employee_id', '=', employee_id.id)])
             logging.info("new_date_to%s__-----????????????????????????????????????????????????????????-----------",new_date_to)
             logging.info("new_date_from%s__------??????????????????????????????????????????????----------",new_date_from)


             logging.info("sale__%s__----------------",att_recs)
             filtered_rec=self.found_unwanted_overtime(new_date_from,employee_id.id,att_recs)
             att_recs=attendance_obj.browse(filtered_rec)


             self.create_entry_work_tripday(new_date_from,new_date_to,employee_id)


             date_dic=self.get_date_start_stop(employee_id,new_date_from,"afternoon")
#              leave_work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE100')], limit=1)
             if date_dic['holiday']==True:
                leave_list=self.check_leave_detail(new_date_from,employee_id)
                if leave_list != None:

                    for leave_dic in leave_list:
                        if leave_dic['leave_type']=='full_days':
                                mdate_dic=self.get_date_start_stop(employee_id,new_date_from,"morning")
                                if  mdate_dic.get("start_date",False):
                                    record=self.env['hr.work.entry'].sudo().create({
                                            'contract_id': employee_id.contract_id.id,
                                            'name': "إجازة: %s" % (employee_id.name),
                                            'date_start': mdate_dic['start_date'],
                                            'date_stop':mdate_dic['end_date'],
                                            'employee_id': employee_id.id,
                                            'work_entry_type_id': leave_dic['leave_entry_type'].id,
                                    })
                                ndate_dic=self.get_date_start_stop(employee_id,new_date_from,"afternoon")
            
                                if  ndate_dic.get("start_date",False):
            

                                    record=self.env['hr.work.entry'].sudo().create({
                                            'contract_id': employee_id.contract_id.id,
                                            'name': "إجازة: %s" % (employee_id.name),
                                            'date_start': ndate_dic['start_date'],
                                            'date_stop':ndate_dic['end_date'],
                                            'employee_id': employee_id.id,
                                            'work_entry_type_id': leave_dic['leave_entry_type'].id,
                                    })
                                if leave_dic['leave_type']=='half_day':
                                    
                                    if leave_dic['leave_period']=='morning':
                                        ndate_dic=self.get_date_start_stop(employee_id,new_date_from,"morning")

                                        record=self.env['hr.work.entry'].sudo().create({
                                                'contract_id': employee_id.contract_id.id,
                                                'name': "إجازة: %s" % (employee_id.name),
                                                'date_start': ndate_dic['start_date'],
                                                'date_stop':ndate_dic['end_date'],
                                                'employee_id': employee_id.id,
                                                'work_entry_type_id': leave_dic['leave_entry_type'].id,
                                        })
                                        created_entry_list.append(record)
                                    if leave_dic['leave_period']=='afternoon':
                                        record=self.env['hr.work.entry'].sudo().create({
                                                'contract_id': employee_id.contract_id.id,
                                                'name': "إجازة: %s" % (employee_id.name),
                                                'date_start': date_dic['start_date'],
                                                'date_stop':date_dic['end_date'],
                                                'employee_id': employee_id.id,
                                                'work_entry_type_id': leave_dic['leave_entry_type'].id,
                                        })
                                        created_entry_list.append(record)                           
             leave_list=self.check_leave_detail(new_date_from,employee_id)
             logging.info("leave_list--------------------leave_list----------------------------%s",leave_list)
             if leave_list != None:
                for leave_dic in leave_list:
                    logging.info("dic------------------------------------------------%s",leave_dic)
                    if leave_dic.get('leave_type',False):
                        if leave_dic['leave_type']=='custom_hours':
                                logging.info("dic------------------------------------------------%s",leave_dic)
                                old_tz = pytz.timezone('UTC')
                                new_tz = pytz.timezone(self.env.user.tz)
                                leave_start_date=new_date_from+relativedelta(hours=float(leave_dic['leave_hour_from']), minutes=0, seconds=0)
                                leave_end_date=new_date_from+relativedelta(hours=float(leave_dic['leave_hour_to']), minutes=0, seconds=0)
                                record=self.env['hr.work.entry'].sudo().create({
                                        'contract_id': employee_id.contract_id.id,
                                        'name': "إجازة: %s" % (employee_id.name),
                                        'date_start':fields.Datetime.to_string(new_tz.localize(leave_start_date).astimezone(old_tz)),
                                        'date_stop':fields.Datetime.to_string(new_tz.localize(leave_end_date).astimezone(old_tz)),
                                        'employee_id': employee_id.id,
                                        'work_entry_type_id': leave_dic['leave_entry_type'].id,
                                })
                                created_entry_list.append(record) 

             small_id_noon=0
             if len(att_recs):
                 no_break=False

                 for atts in att_recs:
                     if atts.no_break:
                        #  check_out=atts.check_out
                         no_break=True
                 if no_break:
                    aft_list=[]
                    for atts in att_recs:
                        if len(att_recs)==2:
                            if atts.day_period=="morning":
                                #external_handling
                                date_dic=self.get_date_start_stop(employee_id,new_date_from,"morning")

                                logging.info("********************************************%s",date_dic['end_date_not_str']+relativedelta(hours=1, minutes=0, seconds=0))
                                logging.info("**********************************************%s",atts.check_out)
                                if atts.check_out > date_dic['end_date_not_str']+relativedelta(hours=1, minutes=0, seconds=0):
                                            worked_more_then_break_in_morning =True
                                            morning_extra= atts.check_out
                        if atts.day_period=='afternoon':
                            if atts.no_break==False:

                                aft_list.append(atts.id)
                            small_id_noon=aft_list[:1]
                            ##logging.info("small_id_noon----------------------------------------------%s__----------------",small_id_noon)
                
                 if len(att_recs)==1:
                    work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)
                    if att_recs[0].day_period=="morning":
                        date_dic=self.get_date_start_stop(employee_id,new_date_from,"morning")
                        date_dic_noon=self.get_date_start_stop(employee_id,new_date_from,"afternoon")

                        logging.info("date_dic-----------------%s",date_dic)
                        logging.info("new_date_to-----------------%s",new_date_to)

                        if date_dic['holiday']==False:
                            if date_dic.get('start_date_not_str',False):                            
                                if not self.check_multiple_entry_issue_wizard(employee_id.id,'morning',new_date_from,new_date_to):
                                    if new_date_to<=date_dic['start_date_not_str']:
                                            logging.info("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")

                                            record=self.env['hr.work.entry'].sudo().create({
                                                'contract_id': employee_id.contract_id.id,
                                                'name': "غائب: %s" % (employee_id.name),
                                                'date_start': date_dic['start_date'],
                                                'date_stop':date_dic['end_date'],
                                                'employee_id': employee_id.id,
                                                'work_entry_type_id': work_entry_type.id,
                                        })
                                            created_entry_list.append(record)

                                logging.info("date_dic['end_date_not_str']))))%s",date_dic['end_date_not_str'])
                                logging.info("att_recs[0].check_out-------------%s",att_recs[0].check_out)

                                if att_recs[0].check_out>date_dic['end_date_not_str']:

                                    if date_dic_noon.get('end_date_not_str',False):
                                        if date_dic_noon['end_date_not_str'] > att_recs[0].check_out:
                                            if not att_recs.excuse_check_out:
                                                    logging.info("mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")
                                                    work_entry_type_list=[work_entry_type.id]
                                                    entry_type_obj=self.env['hr.work.entry.type']
                                                    leave_ids=entry_type_obj.search([('is_leave','=',True)])
                                                    for leave in leave_ids:
                                                        work_entry_type_list.append(leave.id)

                                                    exm=self.env['hr.work.entry'].sudo().search([('contract_id','=',employee_id.contract_id.id),('date_start','=',att_recs[0].check_out),('date_stop','=',date_dic_noon['end_date']),('employee_id','=',employee_id.id),('work_entry_type_id','in',work_entry_type_list)])
                                                    if not len(exm):
                                                        record=self.env['hr.work.entry'].sudo().create({
                                                            'contract_id': employee_id.contract_id.id,
                                                            'name': "خروج مبكر: %s" % (employee_id.name),
                                                            'date_start': att_recs[0].check_out,
                                                            'date_stop':date_dic_noon['end_date'],
                                                            'employee_id': employee_id.id,
                                                            'work_entry_type_id': work_entry_type.id,
                                                    })
                                                        created_entry_list.append(record)
                                else:



                                    if date_dic_noon.get('end_date_not_str',False):
                                            if not att_recs.excuse_check_out:
                                                    logging.info("oooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
                                                    record=self.env['hr.work.entry'].sudo().create({
                                                        'contract_id': employee_id.contract_id.id,
                                                        'name': "خروج مبكر: %s" % (employee_id.name),
                                                        'date_start': date_dic_noon['start_date_not_str'],
                                                        'date_stop':date_dic_noon['end_date_not_str'],
                                                        'employee_id': employee_id.id,
                                                        'work_entry_type_id': work_entry_type.id,
                                                })
                                                    created_entry_list.append(record)

                                    # if date_dic.get('end_date_not_str',False):
                                    #     if date_dic['end_date_not_str'] > att_recs[0].check_out:
                                    #         if not att_recs.excuse_check_out:
                                    #                 record=self.env['hr.work.entry'].sudo().create({
                                    #                     'contract_id': employee_id.contract_id.id,
                                    #                     'name': "خروج مبكر: %s" % (employee_id.name),
                                    #                     'date_start': att_recs[0].check_out,
                                    #                     'date_stop':date_dic['end_date_not_str'],
                                    #                     'employee_id': employee_id.id,
                                    #                     'work_entry_type_id': work_entry_type.id,
                                    #             })
                                    #                 created_entry_list.append(record)


                    else:
                        date_dic=self.get_date_start_stop(employee_id,new_date_from,"morning")
                        if date_dic['holiday']==False:

                            if not self.check_multiple_entry_issue_wizard(employee_id.id,'afternoon',new_date_from,new_date_to):
                                record=self.env['hr.work.entry'].sudo().create({
                                    'contract_id': employee_id.contract_id.id,
                                    'name': "غائب: %s" % (employee_id.name),
                                    'date_start': date_dic['start_date'],
                                    'date_stop':date_dic['end_date'],
                                    'employee_id': employee_id.id,
                                    'work_entry_type_id': work_entry_type.id,
                                })
                                created_entry_list.append(record)


                 for rec in att_recs:
                     print("workkkkkkkkkkkkkkkk%s",rec.day_period)
                     for recs in att_recs:
                        # ##logging.info("day perid%s",rec.day_period)
                        # ##logging.info("day perid%s",rec.id)


                        if recs.day_period =="morning":
                            date_dic=self.get_date_start_stop(employee_id,new_date_from,"morning")
                            ##logging.info("date_dic=========)))))))))))))))))))))))))))))))))))))))))))%s",date_dic)

                            if date_dic.get('start_date_not_str',False):

                                if recs.check_in < date_dic['start_date_not_str']:
                                            early_check_in =True
                                            ##logging.info("rec.check_in=========)))))))))))))))))))))))))))))))))))))))))))%s",recs.check_in)


                     if rec.day_period =="morning":
                        date_dic=self.get_date_start_stop(employee_id,new_date_from,"morning")
                        if date_dic['holiday']==False:
                            logging.info("rec.check_in=========%s",rec.check_in)
                            logging.info("early_check_in------------------%s",early_check_in)
                            logging.info("rec.date_dic['start_date_not_str']=========%s",date_dic['start_date_not_str'])
                            if date_dic.get('start_date_not_str',False):
                           



                                if rec.check_in < date_dic['start_date_not_str']:
                                            early_check_in =True
                                            ##logging.info("rec.check_in=========)))))))))))))))))))))))))))))))))))))))))))%s",rec.check_in)


                                if rec.check_in > date_dic['start_date_not_str']:
                                            ##logging.info("!!!!!!!!!!!!!!!!!!!!!!")
                                            work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)
                                            if not rec.excuse_check_in:
                                                if not self.check_multiple_entry_issue_wizard(employee_id.id,'morning',new_date_from,new_date_to) or rec.excuse_check_out:
                                                    ##logging.info("Iddddddddddddddddddddddddddddss%s",rec.id)
                                                    ##logging.info("early_check_in%s",early_check_in)

                                                    if not early_check_in:
                                                        work_entry_type_list=[work_entry_type.id]
                                                        entry_type_obj=self.env['hr.work.entry.type']
                                                        leave_ids=entry_type_obj.search([('is_leave','=',True)])
                                                        for leave in leave_ids:
                                                            work_entry_type_list.append(leave.id)

                                                        
                                                        exm=self.env['hr.work.entry'].sudo().search([('contract_id','=',rec.employee_id.contract_id.id),('date_start','=',date_dic['start_date']),('date_stop','=',rec.check_in),('employee_id','=',rec.employee_id.id),('work_entry_type_id','in',work_entry_type_list)])
                                                        if not len(exm):

                                                            record = self.env['hr.work.entry'].sudo().create({
                                                                'contract_id': rec.employee_id.contract_id.id,
                                                                'name': "متأخر %s" % (rec.employee_id.name),
                                                                'date_start':date_dic['start_date'],
                                                                'date_stop': rec.check_in ,
                                                                'work_entry_type_id': work_entry_type.id,
                                                                'employee_id': rec.employee_id.id,
                                                            })
                                                            created_entry_list.append(record)
                            if date_dic.get('end_date_not_str',False):
                                if rec.check_out < date_dic['end_date_not_str']:
                                        #logging.info("rec.check_out=========%s",rec.check_out)
                                        #logging.info("rec.date_dic['end_date']=========%s",date_dic['end_date'])
                                        if not rec.excuse_check_out:
                                                    if not self.check_multiple_entry_issue_wizard(employee_id.id,'morning',new_date_from,new_date_to):
                                                                if not rec.no_break:
                                                                    ##logging.info("Idddddddddddddddddddddddddddd morninggg%s",rec.id)

                                                                    work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)
                                                                    if date_dic.get('start_date_not_str',False):

                                                                        if  rec.check_out >date_dic['start_date_not_str']:
                                                                            if not no_break:

                                                                                ex=self.env['hr.work.entry'].sudo().search([('contract_id','=',rec.employee_id.contract_id.id),('name','=',"خروج مبكر %s" % (rec.employee_id.name)),('date_start','=',rec.check_out),('date_stop','=',date_dic['end_date']),('employee_id','=',rec.employee_id.id),('work_entry_type_id','=',work_entry_type.id)])
                                                                                if not len(ex):
                                                                                    record = self.env['hr.work.entry'].sudo().create({
                                                                                        'contract_id': rec.employee_id.contract_id.id,
                                                                                        'name': "خروج مبكر1 %s" % (rec.employee_id.name),
                                                                                        'date_start': rec.check_out,
                                                                                        'date_stop': date_dic['end_date'],
                                                                                        'employee_id': rec.employee_id.id,
                                                                                        'work_entry_type_id': work_entry_type.id,
                                                                                    })
                                                                                    created_entry_list.append(record)

                

                     ##logging.info("rec.day_period==================%s",rec.day_period)
                     if rec.day_period =="afternoon":
                        date_dic=self.get_date_start_stop(employee_id,new_date_from,"afternoon")
                        if date_dic['holiday']==False:
                            if date_dic.get('start_date_not_str',False):

                                if rec.check_in > date_dic['start_date_not_str']:
                                            work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)
                                            if not rec.excuse_check_in:
                                                if not self.check_multiple_entry_issue_wizard(employee_id.id,'afternoon',new_date_from,new_date_to):
                                                    
                                                        if not no_break:
                                                            record = self.env['hr.work.entry'].sudo().create({
                                                                'contract_id': rec.employee_id.contract_id.id,
                                                                'name': "متأخر %s" % (rec.employee_id.name),
                                                                'date_start':date_dic['start_date'],
                                                                'date_stop': rec.check_in ,
                                                                'employee_id': rec.employee_id.id,
                                                                'work_entry_type_id': work_entry_type.id,
                                                            })
                                                            created_entry_list.append(record)

                                                        # ##logging.info("rec.day_period===== small_id_noon=============%s", small_id_noon)

                                                        if  small_id_noon!=0:
                                                            if not worked_more_then_break_in_morning:
                                                                record = self.env['hr.work.entry'].sudo().create({
                                                                    'contract_id': rec.employee_id.contract_id.id,
                                                                    'name': "متأخر %s" % (rec.employee_id.name),
                                                                    'date_start':date_dic['start_date'],
                                                                    'date_stop': rec.check_in ,
                                                                    'employee_id': rec.employee_id.id,
                                                                    'work_entry_type_id': work_entry_type.id,
                                                                })
                                                                created_entry_list.append(record)
                                                            if worked_more_then_break_in_morning:
                                                                record = self.env['hr.work.entry'].sudo().create({
                                                                    'contract_id': rec.employee_id.contract_id.id,
                                                                    'name': "غير متواجد: %s" % (rec.employee_id.name),
                                                                    'date_start':morning_extra,
                                                                    'date_stop': rec.check_in ,
                                                                    'employee_id': rec.employee_id.id,
                                                                    'work_entry_type_id': work_entry_type.id,
                                                                })
                                                                created_entry_list.append(record)



                            if date_dic.get('end_date_not_str',False):

                                if rec.check_out < date_dic['end_date_not_str']:

                                        #logging.info("rec.check_out=========%s",rec.check_out)
                                        #logging.info("rec.date_dic['end_date']=========%s",date_dic['end_date'])
                                        if not rec.excuse_check_out:
                                                    if not self.check_multiple_entry_issue_wizard(employee_id.id,'afternoon',new_date_from,new_date_to):
                                                        work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)
                                                        ##logging.info("rec.check_out=========%s",rec.id)
                                                        record = self.env['hr.work.entry'].sudo().create({
                                                            'contract_id': rec.employee_id.contract_id.id,
                                                            'name': "خروج مبكر %s" % (rec.employee_id.name),
                                                            'date_start': rec.check_out,
                                                            'date_stop':  date_dic['end_date'],
                                                            'employee_id': rec.employee_id.id,
                                                            'work_entry_type_id': work_entry_type.id,
                                                        })  
                                                        created_entry_list.append(record)

                                         
            

             else:
                    day_period = 'morning'

                    work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'LEAVE90')], limit=1)

                    date_dic=self.get_date_start_stop(employee_id,new_date_from,day_period)
                    if date_dic['holiday']==False:
                        if not self.check_multiple_entry_issue_wizard(employee_id.id,day_period,new_date_from,new_date_to):

                            record=self.env['hr.work.entry'].sudo().create({
                                'contract_id': employee_id.contract_id.id,
                                'name': "غائب: %s" % (employee_id.name),
                                'date_start': date_dic['start_date'],
                                'date_stop': date_dic['end_date'],
                                'employee_id': employee_id.id,
                                'work_entry_type_id': work_entry_type.id,
                            })
                            created_entry_list.append(record)

                    day_period = 'afternoon'
                    date_dic=self.get_date_start_stop(employee_id,new_date_from,day_period)
                    if date_dic['holiday']==False:
                        if not self.check_multiple_entry_issue_wizard(employee_id.id,day_period,new_date_from,new_date_to):

                            record=self.env['hr.work.entry'].sudo().create({
                                'contract_id': employee_id.contract_id.id,
                                'name': "غائب: %s" % (employee_id.name),
                                'date_start': date_dic['start_date'],
                                'date_stop':date_dic['end_date'],
                                'employee_id': employee_id.id,
                                'work_entry_type_id': work_entry_type.id,
                            })
                            created_entry_list.append(record)

             next_count+=1
             cnt+=1
            #  logging.info("entries========================%s",entries)

            #  self.manage_conflict_entries(employee_id.contract_id,employee_id,created_entry_list,new_date_from)
             if entries_two!=False and entries_one!=False:
                all_list=created_entry_list+entries_one+entries_two

             if entries_two!=False and entries_one==False:
                all_list=created_entry_list+entries_two

             if entries_two==False and entries_one!=False:
                all_list=created_entry_list+entries_one

             if entries_two==False and entries_one==False:
                all_list=created_entry_list
                
             self.make_attendance(employee_id.contract_id,employee_id,all_list,new_date_from)
             all_list=[]
        action = self.env.ref('hr_work_entry.hr_work_entry_action').sudo().read()[0]
        return action

    def  make_attendance(self,contract,employee,entry_list,new_date_from):
        noon_date_dic=self.env['late.regeneration.wizard'].get_date_start_stop(employee,new_date_from,"afternoon")
        morning_date_dic=self.env['late.regeneration.wizard'].get_date_start_stop(employee,new_date_from,"morning")
        morning_entries=[]
        noon_entries=[]
        bool_val=False
        work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'WORK100')], limit=1)


        #diff noon and morning entries
        logging.info("entry_list========================%s",entry_list)
        
        for entry in entry_list:
                logging.info("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%s",morning_date_dic)
                if morning_date_dic.get('holiday',False) !=True:
                    if entry.date_stop <= morning_date_dic['end_date_not_str']:
                        if morning_date_dic.get('start_date_not_str',False) and morning_date_dic.get('end_date_not_str',False) :

                             morning_entries.append(entry)
                    else:
                            logging.info("morning_date_dic===sss=====================%s",noon_date_dic)

                            if noon_date_dic.get('start_date_not_str',False) and noon_date_dic.get('end_date_not_str',False) :
                                noon_entries.append(entry)
        logging.info("000000000000000000000000000000000000%s",noon_entries)
          
        logging.info("000000000000000000000000000000000000%s",morning_entries)
        logging.info("morning_date_dic========================%s",morning_date_dic)

        logging.info("morning_date_dic========================%s",noon_date_dic)

        if len(noon_entries)>1 and not len(morning_entries):
            record=self.env['hr.work.entry'].sudo().create({
                            'contract_id': contract.id,
                            'name': "حضور: %s" % (employee.name),
                            'date_start':morning_date_dic['start_date_not_str'] ,
                            'date_stop':morning_date_dic['end_date_not_str'] ,
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
            })

        if len(noon_entries)==1 and not len(morning_entries):
            record=self.env['hr.work.entry'].sudo().create({
                            'contract_id': contract.id,
                            'name': "حضور: %s" % (employee.name),
                            'date_start':morning_date_dic['start_date_not_str'] ,
                            'date_stop':morning_date_dic['end_date_not_str'] ,
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
                        }) 
            if  noon_date_dic['start_date_not_str']<noon_entries[0].date_start and  noon_date_dic['end_date_not_str']<=noon_entries[0].date_stop: 
                    record=self.env['hr.work.entry'].sudo().create({
                            'contract_id': contract.id,
                            'name': "حضور: %s" % (employee.name),
                            'date_start': noon_date_dic['start_date_not_str'],
                            'date_stop':noon_entries[0].date_start,
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
                        })
            if  noon_date_dic['start_date_not_str']>=noon_entries[0].date_start and  noon_date_dic['end_date_not_str']>noon_entries[0].date_stop: 
                    record=self.env['hr.work.entry'].sudo().create({
                            'contract_id': contract.id,
                            'name': "حضور: %s" % (employee.name),
                            'date_start':noon_entries[0].date_stop ,
                            'date_stop':noon_date_dic['end_date_not_str'] ,
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
                        }) 
            if  noon_date_dic['start_date_not_str']<noon_entries[0].date_start and  noon_date_dic['end_date_not_str']>noon_entries[0].date_stop: 
                    record=self.env['hr.work.entry'].sudo().create({
                            'contract_id': contract.id,
                            'name': "حضور: %s" % (employee.name),
                            'date_start': noon_date_dic['start_date_not_str'],
                            'date_stop': noon_entries[0].date_start,
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
                        })            

                    record=self.env['hr.work.entry'].sudo().create({
                            'contract_id': contract.id,
                            'name': "حضور: %s" % (employee.name),
                            'date_start': noon_entries[0].date_stop,
                            'date_stop': noon_date_dic['end_date_not_str'],
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
                        }) 

        #check if person works in one shift
        if len(morning_entries)==1 and not len(noon_entries):

                logging.info("000000000000000000morning_date_dic000000000000000000%s",morning_date_dic)
                logging.info("00000000000000000000000nooo0000000000000%s",noon_date_dic)

                if morning_date_dic['start_date_not_str'] < morning_entries[0].date_start and  morning_entries[0].date_stop >= morning_date_dic['end_date_not_str_plus_break'] and morning_entries[0].date_stop >= noon_date_dic['end_date_not_str']  :
                    record=self.env['hr.work.entry'].sudo().create({
                            'contract_id': contract.id,
                            'name': "حضور: %s" % (employee.name),
                            'date_start': morning_entries[0].date_stop,
                            'date_stop':morning_date_dic['end_date_not_str'],
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
                        })
                    if  noon_date_dic.get('holiday',False) !=True:

                        record=self.env['hr.work.entry'].sudo().create({
                                'contract_id': contract.id,
                                'name': "حضور: %s" % (employee.name),
                                'date_start': noon_date_dic['start_date_not_str'],
                                'date_stop':noon_date_dic['end_date_not_str'],
                                'employee_id': employee.id,
                                'work_entry_type_id': work_entry_type.id,
                            })  
                if  noon_date_dic.get('holiday',False) !=True:
         
                    if noon_date_dic['end_date_not_str'] > morning_entries[0].date_stop and  morning_entries[0].date_start <= morning_date_dic['start_date_not_str'] :
                        logging.info("morning_entries[0].date_start========================%s",morning_entries[0].date_stop)
                        logging.info("morning_entries[0].date_start=============morning_date_dic['end_date_not_str']===========????????????????????%s",morning_date_dic)
                        if morning_entries[0].date_stop< morning_date_dic['end_date_not_str']:
                            record=self.env['hr.work.entry'].sudo().create({
                                    'contract_id': contract.id,
                                    'name': "حضور: %s" % (employee.name),
                                    'date_start': morning_entries[0].date_stop,
                                    'date_stop':morning_date_dic['end_date_not_str'],
                                    'employee_id': employee.id,
                                    'work_entry_type_id': work_entry_type.id,
                                })
                    if not noon_date_dic.get('holiday',False):

                        record=self.env['hr.work.entry'].sudo().create({
                                'contract_id': contract.id,
                                'name': "حضور: %s" % (employee.name),
                                'date_start': noon_date_dic['start_date_not_str'],
                                'date_stop':noon_date_dic['end_date_not_str'],
                                'employee_id': employee.id,
                                'work_entry_type_id': work_entry_type.id,
                            }) 
                # logging.info("noon_date_dic['end_date_not_str'========================%s",noon_date_dic['end_date_not_str'])
                # logging.info("morning_entries[0].date_stop========================%s",morning_entries[0].date_stop)
                # logging.info("morning_date_dic['start_date_not_str']========================%s",morning_date_dic['start_date_not_str'])
        logging.info("morning_entries[0].date_start========================%s",morning_date_dic)
        if len(morning_entries) > 1 and not len(noon_entries):
                
                if not noon_date_dic.get('holiday',False):

                    record=self.env['hr.work.entry'].sudo().create({
                            'contract_id': contract.id,
                            'name': "حضور: %s" % (employee.name),
                            'date_start': noon_date_dic['start_date_not_str'],
                            'date_stop':noon_date_dic['end_date_not_str'],
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
                        })
        if len(morning_entries) > 1:
            end_date=False
            #logging.info("morning_entries========================%s",morning_entries)
            dic={}
            list=[]
            new_list=[]
            id_list=[]
            new_morning_entries=[]
            for e in morning_entries:
                list.append(e.date_start)
                id_list.append(e.id)
            #logging.info("list========================%s", min(list))

            while len(list):
                new_list.append(min(list))
                list.remove(min(list))

            for el  in new_list:
                rec=self.env['hr.work.entry'].search([('id','in',id_list),('date_start','=',el)],limit=1)
                new_morning_entries.append(rec)
            logging.info("new_morning_entries========================%s",new_morning_entries)

            for entry in new_morning_entries:
                    # if entry.date_stop >= morning_date_dic['end_date_not_str']:
                    #     continue
                    # self.env.cr.commit()
                    logging.info("entry========================%s",entry)
                    #logging.info("end_date========================%s",entry.id)
                    #logging.info("end_date========================%s",entry.date_start)

                    if end_date:
                        if end_date<entry.date_start:
                            record=self.env['hr.work.entry'].sudo().create({
                                'contract_id': contract.id,
                                'name': "حضور: %s" % (employee.name),
                                'date_start': end_date,
                                'date_stop':entry.date_start,
                                'employee_id': employee.id,
                                'work_entry_type_id': work_entry_type.id,
                            })
                    else:
                        if entry.date_start>morning_date_dic['start_date_not_str']:
                            record=self.env['hr.work.entry'].sudo().create({
                                'contract_id': contract.id,
                                'name': "حضور: %s" % (employee.name),
                                'date_start': morning_date_dic['start_date_not_str'],
                                'date_stop':entry.date_start,
                                'employee_id': employee.id,
                                'work_entry_type_id': work_entry_type.id,
                            })

                    end_date=entry.date_stop

        if len(noon_entries) > 1:
            end_date=False
            #logging.info("morning_entries========================%s",morning_entries)
            dic={}
            list=[]
            new_list=[]
            id_list=[]
            new_noon_entries=[]
            for e in noon_entries:
                list.append(e.date_start)
                id_list.append(e.id)
            #logging.info("list========================%s", min(list))

            while len(list):
                new_list.append(min(list))
                list.remove(min(list))

            for el  in new_list:
                rec=self.env['hr.work.entry'].search([('id','in',id_list),('date_start','=',el),('name','not ilike','إجازة')])
                new_noon_entries.append(rec)
            #logging.info("new_morning_entries========================%s",new_morning_entries)            for entry in new_noon_entries:
                    # if entry.date_stop >= noon_date_dic['end_date_not_str']:
                    #     continue
            logging.info("new_noon_entries========================%s",new_noon_entries)
       
            for entry in new_noon_entries:


                if end_date:
                    if entry.date_start!= end_date:
                        logging.info("entry.date_start========================%s",entry.date_start)
                        logging.info("end_date========================%s",end_date)
                        record=self.env['hr.work.entry'].sudo().create({
                            'contract_id': contract.id,
                            'name': "حضور: %s" % (employee.name),
                            'date_start':end_date,
                            'date_stop':entry.date_start,
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
                        })

                else:
                    logging.info("new_noon_entries========================%s",entry)
                    logging.info("new_noon_entries========================%s",entry)

                    if entry.date_start!= noon_date_dic['start_date_not_str']:

                        record=self.env['hr.work.entry'].sudo().create({
                            'contract_id': contract.id,
                            'name': "حضور: %s" % (employee.name),
                            'date_start': noon_date_dic['start_date_not_str'],
                            'date_stop':entry.date_start,
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
                        })
                end_date=entry.date_stop
                logging.info("end_date=========stoooooooooooo===============%s",end_date)
            if end_date:
                if end_date < noon_date_dic['end_date_not_str']: 
                    record=self.env['hr.work.entry'].sudo().create({
                        'contract_id': contract.id,
                        'name': "حضور: %s" % (employee.name),
                        'date_start': end_date,
                        'date_stop':noon_date_dic['end_date_not_str'],
                        'employee_id': employee.id,
                        'work_entry_type_id': work_entry_type.id,
                    })






        if not len(morning_entries) and not len(noon_entries):
            if morning_date_dic['holiday'] !=True:
                record=self.env['hr.work.entry'].sudo().create({
                'contract_id': contract.id,
                'name': "حضور: %s" % (employee.name),
                'date_start': morning_date_dic['start_date_not_str'],
                'date_stop': morning_date_dic['end_date_not_str'],
                'employee_id': employee.id,
                'work_entry_type_id': work_entry_type.id,
            })

        # if not len(noon_entries):
            if morning_date_dic['holiday'] !=True:

                record=self.env['hr.work.entry'].sudo().create({
                'contract_id': contract.id,
                'name': "حضور: %s" % (employee.name),
                'date_start': noon_date_dic['start_date_not_str'],
                'date_stop': noon_date_dic['end_date_not_str'],
                'employee_id': employee.id,
                'work_entry_type_id': work_entry_type.id,
            })
            # if bool_val:
            #     return True
        if len(morning_entries) ==1 and len(noon_entries):

            if morning_entries[0].date_start>morning_date_dic['start_date_not_str'] and morning_entries[0].date_stop <morning_date_dic['end_date_not_str']:

                record=self.env['hr.work.entry'].sudo().create({
                            'contract_id': contract.id,
                            'name': "حضور: %s" % (employee.name),
                            'date_start': morning_date_dic['start_date_not_str'],
                            'date_stop':morning_entries[0].date_start,
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
                        })

                record=self.env['hr.work.entry'].sudo().create({
                        'contract_id': contract.id,
                        'name': "حضور: %s" % (employee.name),
                            'date_start':morning_entries[0].date_stop,
                            'date_stop':morning_date_dic['end_date_not_str'],
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
                        })

            if morning_entries[0].date_start>morning_date_dic['start_date_not_str'] and morning_entries[0].date_stop >= morning_date_dic['end_date_not_str']:

                record=self.env['hr.work.entry'].sudo().create({
                            'contract_id': contract.id,
                            'name': "حضور: %s" % (employee.name),
                            'date_start': morning_date_dic['start_date_not_str'],
                            'date_stop':morning_entries[0].date_start,
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
                        })

            if morning_entries[0].date_start<=morning_date_dic['start_date_not_str'] and morning_entries[0].date_stop < morning_date_dic['end_date_not_str']:
                
                record=self.env['hr.work.entry'].sudo().create({
                            'contract_id': contract.id,
                            'name': "حضور: %s" % (employee.name),
                            'date_start':morning_entries[0].date_stop,
                            'date_stop':morning_date_dic['end_date_not_str'],
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
                        })


        if len(noon_entries) ==1 and len(morning_entries):
            

            if noon_entries[0].date_start>noon_date_dic['start_date_not_str'] and noon_entries[0].date_stop <noon_date_dic['end_date_not_str']:

                record=self.env['hr.work.entry'].sudo().create({
                            'contract_id': contract.id,
                            'name': "حضور: %s" % (employee.name),
                            'date_start': noon_date_dic['start_date_not_str'],
                            'date_stop':noon_entries[0].date_start,
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
                        })

                record=self.env['hr.work.entry'].sudo().create({
                        'contract_id': contract.id,
                        'name': "حضور: %s" % (employee.name),
                            'date_start':noon_entries[0].date_stop,
                            'date_stop':noon_date_dic['end_date_not_str'],
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
                        })

            if noon_entries[0].date_start>noon_date_dic['start_date_not_str'] and noon_entries[0].date_stop >= noon_date_dic['end_date_not_str']:

                record=self.env['hr.work.entry'].sudo().create({
                            'contract_id': contract.id,
                            'name': "حضور: %s" % (employee.name),
                            'date_start': noon_date_dic['start_date_not_str'],
                            'date_stop':noon_entries[0].date_start,
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
                        })

            if noon_entries[0].date_start<=noon_date_dic['start_date_not_str'] and noon_entries[0].date_stop < noon_date_dic['end_date_not_str']:
                
                record=self.env['hr.work.entry'].sudo().create({
                            'contract_id': contract.id,
                            'name': "حضور: %s" % (employee.name),
                            'date_start':noon_entries[0].date_stop,
                            'date_stop':noon_date_dic['end_date_not_str'],
                            'employee_id': employee.id,
                            'work_entry_type_id': work_entry_type.id,
                        })


        return
