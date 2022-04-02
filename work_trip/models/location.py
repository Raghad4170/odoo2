from odoo import api, fields, models, tools, exceptions, _
_AVG_EARTH_RADIUS_KM = 6371.0088


from math import radians, cos, sin, asin, sqrt

from odoo.exceptions import AccessError, UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)



class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def attendance_post(self, next_action, entered_pin=False, location=False):
        res = super(HrEmployee, self.with_context(attendance_location=location)).attendance_manual(next_action, entered_pin)
        return res

    def _attendance_action_change(self):
        res = super()._attendance_action_change()
        location = self.env.context.get('attendance_location', False)
        if location:
            if self.attendance_state == 'checked_in':
                away_location=False
                for allowed_location in self.user_id.allowed_locations:
                       allowed_latitude=float(allowed_location.check_in_latitude)
                       allowed_longitude=float(allowed_location.check_in_longitude)
                       entered_allowed_latitude= location[0]
                       entered_allowed_longitude=location[1]
                       if (allowed_latitude!=entered_allowed_latitude) and (allowed_longitude!=entered_allowed_longitude):
                           location_one=tuple([allowed_latitude,allowed_longitude])
                           location_two=tuple([entered_allowed_latitude,entered_allowed_longitude])
                           lat1, lng1 = location_one
                           lat2, lng2 = location_two
                           lat1 = radians(lat1)
                           lng1 = radians(lng1)
                           lat2 = radians(lat2)
                           lng2 = radians(lng2)

                            # calculate haversine
                           lat = lat2 - lat1
                           lng = lng2 - lng1
                           d = sin(lat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(lng * 0.5) ** 2
                           calculated_meteres=2 * (_AVG_EARTH_RADIUS_KM*1000.0) * asin(sqrt(d))

                           if calculated_meteres < allowed_location.attendance_range:
                                 away_location=False
                                 break
                           else:
                               away_location=True
                                 
                if away_location:
                    raise exceptions.UserError(_('لا يمكنك تسجيل الدخول من موقعك الحالي'))

                res.write({'check_in_latitude': location[0],'check_in_longitude': location[1], 'check_in_maps': "https://www.google.com/maps/search/{latitude},{longitude}/@{latitude},{longitude}".format(latitude=location[0],longitude=location[1])})
            else:
                res.write({ 'check_out_latitude': location[0],'check_out_longitude': location[1],'check_out_maps': "https://www.google.com/maps/search/{latitude},{longitude}/@{latitude},{longitude}".format(latitude=location[0],longitude=location[1])})
        return res
    
class HrAttendance(models.Model):
    _inherit = "hr.attendance"
    
    check_in_latitude = fields.Char("CheckIn Latitude",readonly=True)
    check_in_longitude = fields.Char("CheckIn Longitude",readonly=True)
    check_in_maps = fields.Char("موقع تسجيل الدخول", readonly=True)
    check_out_latitude = fields.Char("CheckOut Latitude",readonly=True)
    check_out_longitude = fields.Char("CheckOut Longitude",readonly=True)
    check_out_maps = fields.Char("موقع تسجيل الخروج", readonly=True)
