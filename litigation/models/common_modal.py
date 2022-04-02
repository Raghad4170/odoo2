# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
import dateutil
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta 
import logging
_logger = logging.getLogger(__name__)

class common_modal(models.Model):
    _name = 'common.modal'
    _description = 'common modal'


    def check_updation(self,modal):
        modal_obj=self.env[modal]
        records=modal_obj.sudo().search([('state','not in',('close','suspended'))])
        for record in records:
            today = date.today()
            leave = self.env['hr.leave'].sudo().search([('request_date_from', '<=', today),
                                                 ('request_date_to', '>=', today),
                                                 ('employee_id', '=', record.user_id.employee_id.id),
                                                 ('state','=','validate')])
            if len(leave):
                return
            else:
                dateTimeDifference=datetime.now()-record.write_date
                dateTimeDifferenceInHours = float(dateTimeDifference.total_seconds() / 3600)
                if dateTimeDifferenceInHours >48:
                    url = record.url
                    body_html = ("لم يتم تحديث سجل: " + record.name + " لمدة 48 ساعة يرجى الإطلاع ومتابعة السجل " + '<div>.</div>' + '<a href="%s"style="padding: 8px 16px 8px 16px; border-radius: 3px; background-color:#875A7B; text-align:center; text-decoration:none; color: #FFFFFF;">للإطلاع</a>' % url)
                    vals = {
                        'subject': "لم يتم تحديث السجل لمدة 48 ساعة",
                        'body_html': body_html,
                        'author_id': record.user_id.partner_id.id,
                        'email_from': record.user_id.company_id.partner_id.email_formatted or record.user.email_formatted,
                        'email_to':record.user_id.partner_id.email,
                        'auto_delete': True,
                        'state': 'outgoing'
                    }
                    self.env['mail.mail'].sudo().create(vals).send()
