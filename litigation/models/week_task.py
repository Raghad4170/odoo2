from odoo import models, fields, api
from datetime import datetime, timedelta, date


class employeesinfo(models.Model):
    _inherit = 'hr.employee'

    week_report = fields.Boolean('التقارير الأسبوعية للمهام', groups="hr.group_hr_user", store=True)
    week_task_count = fields.Integer(string='عدد مهام الأسبوع', groups="hr.group_hr_user", compute='get_week_task')
    week_task = fields.Html(string='مهام الأسبوع', groups="hr.group_hr_user", compute='get_week_task')

    def get_week_task(self):
        for employee in self:
            week_task = ''
            user = employee.user_id
            today = date.today()
            aweek = today + timedelta(days = 6)
            tasks = self.env['project.task'].sudo().search([('user_id','=',user.id),('date_deadline','<=', aweek),('state_id','!=', 'منتهية')])
            employee.week_task_count = len(tasks) 
            for task in tasks:
                effective_hours = timedelta(hours=task.effective_hours)
                week_task += ("<tr><td style='text-align: center'>" + task.name + "</td><td style='text-align: center'>" + task.following_to + "</td><td style='text-align: center'>" + str(task.create_date.date()) 
                              + "</td><td style='text-align: center'>" + str(effective_hours) + "</td><td style='text-align: center'>" + task.state_id + "</td><td style='text-align: center'>" + str(task.date_deadline) + "</td></tr>")
            employee.week_task = ("<table class='table table-bordered'><tbody><tr><td style='text-align: center'>المهمة</td><td style='text-align: center'>تابعة إلى</td><td style='text-align: center'>التاريخ</td>" +
                                  "<td style='text-align: center'>الوقت المستغرق</td><td style='text-align: center'>الحالة</td><td style='text-align: center'>الموعد النهائي</td></tr>" + week_task + "</tbody></table>")

    def send_week_task(self):
        employees = self.env['hr.employee'].sudo().search([('week_report','!=', False),('gender','!=', False)])
        for employee in employees:
            if employee.gender == 'female':
                mail_template = self.env.ref('litigation.send_week_task_female')
                mail_template.send_mail(employee.id, force_send=True, notif_layout='mail.mail_notification_light')
                send_mail=True
            elif employee.gender == 'male':
                mail_template = self.env.ref('litigation.send_week_task_male')
                mail_template.send_mail(employee.id, force_send=True, notif_layout='mail.mail_notification_light')
                send_mail=True

