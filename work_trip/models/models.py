# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, exceptions, _
from odoo.http import request
from odoo.exceptions import AccessError, UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class AllowedIPs(models.Model):
    _name = 'allowed.ips'
    _description = 'allowed ips'

    users_ip = fields.Many2one('res.users', string='IP')
    ip_address = fields.Char(string='عنوان بروتوكول الإنترنت')
    
class Location(models.Model):
    _name = 'allowed.location'
    _description = 'allowed location'

    users_location = fields.Many2one('res.users', string='الموقع')
    check_in_latitude = fields.Char("خط العرض")
    check_in_longitude = fields.Char("خط الطول")
    attendance_range=fields.Integer("المدى المسموح به بالمتر")
    
class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    allowed_ips = fields.One2many('allowed.ips', 'users_ip', string='IP')
    allowed_locations = fields.One2many('allowed.location', 'users_location', string='المواقع المسموح بها')
        
    def submit_coordinates(self,user_id,lat,lng,meter):
        self.env['allowed.location'].sudo().create(
            {'users_location':user_id,'check_in_latitude':lat,'check_in_longitude':lng,'attendance_range':meter})
        return True
    
    def set_map(self):
        return {
                'type': 'ir.actions.client',
                'tag': 'hr_attendance_action_map',
                'context': {'user_id':self.id},
                'target': 'new',
                }
    
    
class HrAttendance(models.Model):
    _inherit = "hr.attendance"
    
    work_trip = fields.Selection([
        ('attendance', 'حضور'),
        ('late break', 'بريك متأخر'),
        ('Outside meeting', 'حضور اجتماع خارجي'),
        ('court', 'مراجعة المحكمة'),
        ('outside task','مهمة خارجية')], string='نوع الحضور', default='attendance')

    is_trip_entry=fields.Boolean("رحلة عمل")
    excuse_check_in=fields.Boolean("Excuse Check In")
    excuse_check_out=fields.Boolean("Excuse Check Out")
    
class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    trip_state = fields.Selection(related='employee_id.trip_state', readonly=True,
        groups="base.group_user")

class employeesinfo(models.Model):
    _inherit = 'hr.employee'

    trip_state = fields.Selection(string="Trip Status", compute='_compute_trip_state', selection=[('start', "Start"), ('end', "End")], groups="hr.group_hr_user")

    def _compute_trip_state(self):
        for employee in self:
            trip_id = self.env['hr.attendance'].sudo().search([
                ('employee_id', '=', employee.id),('is_trip_entry','=',True)
            ],order='create_date desc', limit=1)
            logging.info("trip_idddd--------------%s",trip_id)

            if not len(trip_id):
                 employee.trip_state='start'
            else:
                if (trip_id.check_in):
                    if not trip_id.check_out:
                         employee.trip_state='end'
                    else:
                         employee.trip_state='start'
                            
    def update_work_trip(self,trip_state,reason, location):
        self.ensure_one()
        action_date = fields.Datetime.now()
        user = self.user_id
        ip_address = request.httprequest.environ['REMOTE_ADDR']
        if self.attendance_state != 'checked_in':
            raise exceptions.UserError(_('يجب عليك تسجيل الدخول لبدء رحلة العمل'))
        if trip_state == 'start':
            attendance_normal = self.env['hr.attendance'].sudo().search([('employee_id', '=', self.id), ('check_out', '=', False)],  order='create_date desc',limit=1)
            if attendance_normal:
                attendance_normal.check_out = action_date
                attendance_normal.excuse_check_out = True
                attendance_normal.check_out_latitude = location[0]
                attendance_normal.check_out_longitude = location[1]
                attendance_normal.check_out_maps = "https://www.google.com/maps/search/{latitude},{longitude}/@{latitude},{longitude}".format(latitude=location[0],longitude=location[1])
                vals = {
                    'employee_id': self.id,
                    'check_in': action_date,
                    'is_trip_entry':True,
                    'work_trip':reason,
                    'check_in_latitude':location[0],
                    'check_in_longitude':location[1],
                    'check_in_maps':"https://www.google.com/maps/search/{latitude},{longitude}/@{latitude},{longitude}".format(latitude=location[0],longitude=location[1]),
                }
                return self.env['hr.attendance'].sudo().create(vals)
        attendance = self.env['hr.attendance'].sudo().search([('employee_id', '=', self.id),('is_trip_entry','=',True), ('check_out', '=', False)],  order='create_date desc',limit=1)
        if attendance:
            if user.allowed_ips:
                ip_list = []
                for self in user.allowed_ips:
                    ip_list.append(self.ip_address)
                if ip_address not in ip_list:
                    raise exceptions.UserError(_('غير مسموح لك بإنهاء رحلة العمل من موقعك الحالي'))
            attendance.check_out = action_date
            attendance.check_out_latitude = location[0]
            attendance.check_out_longitude = location[1]
            attendance.check_out_maps = "https://www.google.com/maps/search/{latitude},{longitude}/@{latitude},{longitude}".format(latitude=location[0],longitude=location[1])
            new_vals = {
                'employee_id': self.id,
                'check_in': action_date,
                'excuse_check_in':True,
                'check_in_latitude':location[0],
                'check_in_longitude':location[1],
                'check_in_maps':"https://www.google.com/maps/search/{latitude},{longitude}/@{latitude},{longitude}".format(latitude=location[0],longitude=location[1]),
            }
            return self.env['hr.attendance'].sudo().create(new_vals)
        return attendance
    
    
    
    def _attendance_action_change(self):
        """ Check In/Check Out action
            Check In: create a new attendance record
            Check Out: modify check_out field of appropriate attendance record
        """
        self.ensure_one()
        action_date = fields.Datetime.now()
        user = self.user_id
        ip_address = request.httprequest.environ['REMOTE_ADDR']
        if self.attendance_state != 'checked_in':           
            vals = {
                'employee_id': self.id,
                'check_in': action_date,
            }
            if user.allowed_ips:
                ip_list = []
                for self in user.allowed_ips:
                    ip_list.append(self.ip_address)
                if ip_address not in ip_list:
                    raise exceptions.UserError(_('غير مسموح لك بالدخول من موقعك الحالي'))
            return self.env['hr.attendance'].create(vals)
        attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '=', False)], limit=1)
        trip = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '=', False), ('is_trip_entry', '=', True)])
        if attendance:
            if trip:
                raise exceptions.UserError(_('يجب عليك إنهاء الرحلة أولا'))
            else:
                if user.allowed_ips:
                    ip_list = []
                    for self in user.allowed_ips:
                        ip_list.append(self.ip_address)
                    if ip_address not in ip_list:
                        raise exceptions.UserError(_('غير مسموح لك بالخروج من موقعك الحالي'))
                attendance.check_out = action_date
        else:
            raise exceptions.UserError(_('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
                'Your attendances have probably been modified manually by human resources.') % {'empl_name': self.sudo().name, })
        return attendance
