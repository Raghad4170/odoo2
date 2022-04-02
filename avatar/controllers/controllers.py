# Copyright to The City Law Firm
import base64
import logging

from odoo.http import content_disposition, Controller, request, route
import odoo.addons.portal.controllers.portal as PortalController
from odoo import exceptions
import datetime
from odoo import http, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError
import requests



class CustomerPortal(PortalController.CustomerPortal):

    def account(self, redirect=None, **post):
        if 'image_1920' in post:
            image_1920 = post.get('image_1920')
            if image_1920:
                image_1920 = image_1920.read()
                image_1920 = base64.b64encode(image_1920)
                request.env.user.partner_id.sudo().write({
                    'image_1920': image_1920
                })
            post.pop('image_1920')
        if 'clear_avatar' in post:
            request.env.user.partner_id.sudo().write({
                'image_1920': False
            })
            post.pop('clear_avatar')
        return super(CustomerPortal, self).account(redirect=redirect, **post)
    
class MyAttendance(http.Controller):
    
    @http.route(['/my/sign_in_attendance'], type='http', auth="user", website=True)
    def sign_in_attendace(self, **post):
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
        check_in = datetime.now().strftime("%Y-%m-%d %H:%M:%S")        
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
            else:
                vals = {
                        'employee_id': employee.id,
                        'check_in': check_in,
                        }
                attendance = request.env['hr.attendance'].sudo().create(vals)
        return request.redirect('/my')


    @http.route(['/my/sign_out_attendance'], type='http', auth="user", website=True)
    def sign_out_attendace(self, **post):
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)])
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
            else:
                no_check_out_attendances = request.env['hr.attendance'].search([
                            ('employee_id', '=', employee.id),
                            ('check_out', '=', False),
                        ])
                check_out = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
                attendance = no_check_out_attendances.write({'check_out':check_out})
        return request.redirect('/my')

    
    
    @http.route(['/website/approve_leave'], type='http', auth="public", methods=['POST'], csrf=False,website=True)
    def approve_leave(self,**kw):
        leave_obj=request.env['hr.leave']
        type_obj = request.env['hr.leave.type']
        employee_obj=request.env['hr.employee']
        emp_id=employee_obj.search([('user_id','=',request.env.uid)])

        if len(emp_id):
            logging.info("----------------------------------%s",emp_id[0].id)
            # try:
            data=type_obj.browse(int(kw['timeoff_type']))
            logging.info("------------------data.request_unit----------------%s",data.request_unit)

            if data.request_unit == 'hour':
                    logging.info("--------kw['date_to']--------------%s",kw)
                    date_time_obj = datetime.strptime(kw['date_from']+' 00:00:00', '%Y-%m-%d %H:%M:%S')
                    x=date_time_obj.date()

                    today_week_day =date.today().weekday()
            
                    user_tz = request.env.user.tz

                    old_tz = pytz.timezone('UTC')
                    new_tz = pytz.timezone(request.env.user.tz)
                    emp=emp_id[0]
             

                    for attendance_day_data in emp.resource_calendar_id.attendance_ids:
                            if attendance_day_data.dayofweek  == str(today_week_day):
                                if kw['request_date_from_period']=='pm':
                                    if attendance_day_data.day_period == 'afternoon':
                                        start_date= x+relativedelta(hours=attendance_day_data.hour_from, minutes=0, seconds=0)
                                        start_date_f =datetime.strptime(new_tz.localize(start_date).astimezone(old_tz).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')

                                        end_date= x+relativedelta(hours=(attendance_day_data.hour_to), minutes=0, seconds=0)
                                        end_date_f =datetime.strptime(new_tz.localize(end_date).astimezone(old_tz).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')
                                if kw['request_date_from_period']=='am':

                                    if attendance_day_data.day_period == 'morning':
                                            start_date= x+relativedelta(hours=attendance_day_data.hour_from, minutes=0, seconds=0)
                                            start_date_f =datetime.strptime(new_tz.localize(start_date).astimezone(old_tz).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')

                                            end_date= x+relativedelta(hours=(attendance_day_data.hour_to), minutes=0, seconds=0)
                                            end_date_f =datetime.strptime(new_tz.localize(end_date).astimezone(old_tz).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')

                
  

                    logging.info("------start_date_f------------%s",start_date_f)
                    
                    logging.info("------end_date_f------------%s",end_date_f)
                    

                    dic={'employee_id':emp_id[0].id,'employee_ids': [(6,0, [emp_id[0].id])],'holiday_status_id':int(kw['timeoff_type']),'request_date_to':end_date_f,'date_from':start_date_f,'date_to':end_date_f,'request_date_from':start_date_f,'holiday_type':'employee','name':kw['description']}
                    if kw.get('day_type',False)=='half_day':
                        dic['request_unit_half']=True
                        dic['request_date_from_period']=kw['request_date_from_period']
                    else:
                        # dic['day_type']='custom_hours'

                        start_date= x+relativedelta(hours=float(kw['from_days']), minutes=0, seconds=0)
                        start_date_f =datetime.strptime(new_tz.localize(start_date).astimezone(old_tz).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')


                        end_date= x+relativedelta(hours=float(kw['to_days']), minutes=0, seconds=0)
                        end_date_f =datetime.strptime(new_tz.localize(end_date).astimezone(old_tz).strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')


                        logging.info("------start_date_f------------%s",start_date_f)
                        
                        logging.info("------end_date_f------------%s",end_date_f)

                        dic['request_date_from_period']=kw['request_date_from_period']
                        dic['request_unit_hours']=False
                        dic['request_hour_to']=kw['to_days']
                        dic['request_hour_from']=kw['from_days']
                        dic['request_date_to']=end_date_f
                        dic['date_from']=start_date_f
                        dic['date_to']=end_date_f
                        dic['request_date_from']=start_date_f
                    logging.info("-----------dic-----------------------%s",dic)

                    leave_obj.create(dic)

            else:
                     leave_obj.create({'employee_id':emp_id[0].id,'employee_ids': [(6,0, [emp_id[0].id])],'holiday_status_id':int(kw['timeoff_type']),'date_from':kw['date_from'],'date_to':kw['date_to'],'request_date_from':kw['date_from'],'request_date_to':kw['date_to'],'number_of_days':float(kw['duration']),'holiday_type':'employee','name':kw['description']})
            logging.info("----------------------------------%s",kw)
            # except Exception as e:
            # logging.info("--------------KKKKKKKKKKKKKKKKKK--------------------%s",e)
                # es
        return request.redirect('/my/home')

    
    

    @http.route(['/my/leave_management'], type='http', auth="user", website=True)
    def leave_management(self, **post):
        timeoff_types=request.env['hr.leave.type'].sudo().search(['|', ('requires_allocation', '=', 'no'), '&', ('has_valid_allocation', '=', True), ('max_leaves', '>', '0')])
        request_hour_to=[
        ('0', '12:00 AM'), ('0.5', '12:30 AM'),
        ('1', '1:00 AM'), ('1.5', '1:30 AM'),
        ('2', '2:00 AM'), ('2.5', '2:30 AM'),
        ('3', '3:00 AM'), ('3.5', '3:30 AM'),
        ('4', '4:00 AM'), ('4.5', '4:30 AM'),
        ('5', '5:00 AM'), ('5.5', '5:30 AM'),
        ('6', '6:00 AM'), ('6.5', '6:30 AM'),
        ('7', '7:00 AM'), ('7.5', '7:30 AM'),
        ('8', '8:00 AM'), ('8.5', '8:30 AM'),
        ('9', '9:00 AM'), ('9.5', '9:30 AM'),
        ('10', '10:00 AM'), ('10.5', '10:30 AM'),
        ('11', '11:00 AM'), ('11.5', '11:30 AM'),
        ('12', '12:00 PM'), ('12.5', '12:30 PM'),
        ('13', '1:00 PM'), ('13.5', '1:30 PM'),
        ('14', '2:00 PM'), ('14.5', '2:30 PM'),
        ('15', '3:00 PM'), ('15.5', '3:30 PM'),
        ('16', '4:00 PM'), ('16.5', '4:30 PM'),
        ('17', '5:00 PM'), ('17.5', '5:30 PM'),
        ('18', '6:00 PM'), ('18.5', '6:30 PM'),
        ('19', '7:00 PM'), ('19.5', '7:30 PM'),
        ('20', '8:00 PM'), ('20.5', '8:30 PM'),
        ('21', '9:00 PM'), ('21.5', '9:30 PM'),
        ('22', '10:00 PM'), ('22.5', '10:30 PM'),
        ('23', '11:00 PM'), ('23.5', '11:30 PM')]
        request_hours_from=[
        ('0', '12:00 AM'), ('0.5', '12:30 AM'),
        ('1', '1:00 AM'), ('1.5', '1:30 AM'),
        ('2', '2:00 AM'), ('2.5', '2:30 AM'),
        ('3', '3:00 AM'), ('3.5', '3:30 AM'),
        ('4', '4:00 AM'), ('4.5', '4:30 AM'),
        ('5', '5:00 AM'), ('5.5', '5:30 AM'),
        ('6', '6:00 AM'), ('6.5', '6:30 AM'),
        ('7', '7:00 AM'), ('7.5', '7:30 AM'),
        ('8', '8:00 AM'), ('8.5', '8:30 AM'),
        ('9', '9:00 AM'), ('9.5', '9:30 AM'),
        ('10', '10:00 AM'), ('10.5', '10:30 AM'),
        ('11', '11:00 AM'), ('11.5', '11:30 AM'),
        ('12', '12:00 PM'), ('12.5', '12:30 PM'),
        ('13', '1:00 PM'), ('13.5', '1:30 PM'),
        ('14', '2:00 PM'), ('14.5', '2:30 PM'),
        ('15', '3:00 PM'), ('15.5', '3:30 PM'),
        ('16', '4:00 PM'), ('16.5', '4:30 PM'),
        ('17', '5:00 PM'), ('17.5', '5:30 PM'),
        ('18', '6:00 PM'), ('18.5', '6:30 PM'),
        ('19', '7:00 PM'), ('19.5', '7:30 PM'),
        ('20', '8:00 PM'), ('20.5', '8:30 PM'),
        ('21', '9:00 PM'), ('21.5', '9:30 PM'),
        ('22', '10:00 PM'), ('22.5', '10:30 PM'),
        ('23', '11:00 PM'), ('23.5', '11:30 PM')]

        request_date_from_period =[
        ('am', 'Morning'), ('pm', 'Afternoon')]
        return request.render("avatar.leave_portal",{'request_date_from_period':request_date_from_period,'timeoff_types':timeoff_types,'request_hours_from':request_hours_from,'request_hours_to':request_hour_to})




    @http.route('/get/time_type', type='json', methods=['POST'], auth="public", website=True)
    def get_doctors_timez(self,timeoff_id):
        type_obj = request.env['hr.leave.type']
        data=type_obj.browse(int(timeoff_id))
        if data.request_unit == 'hour':
            return True
        else:
            return False