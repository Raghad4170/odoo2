import ast
from datetime import datetime, timedelta, date
from random import randint
import uuid
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning
from odoo.tools.misc import format_date, get_lang
from odoo.osv.expression import OR
from werkzeug import urls

class employeesinfo(models.Model):
    _inherit = 'hr.employee'

    sign_signature = fields.Binary(related='user_id.sign_signature', groups="hr.group_hr_user")
    lawyer_manager = fields.Many2one(related='user_id.lawyer_manager', domain=[('share', '=', False)], readonly=False, groups="hr.group_hr_user")
    lawyer_assistants = fields.One2many(related='user_id.lawyer_assistants', domain=[('share', '=', False)], readonly=False, groups="hr.group_hr_user")


class law(models.Model):
    _inherit = 'res.users'
    
    
    lawyer_manager = fields.Many2one('res.users', string='المدير المحامي', domain=[('share', '=', False)])
    lawyer_assistants = fields.One2many('res.users', 'lawyer_manager', string='المساعدون', domain=[('share', '=', False)])
    sign_signature = fields.Binary(string='التوقيع الإلكتروني', readonly=False, groups="base.group_user")
    
    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['lawyer_manager', 'lawyer_assistants', 'sign_signature']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ['sign_signature']
    
class Project(models.Model):
    _inherit = "project.project"

    litigation_ids = fields.One2many('litigation.litigation', 'project_id', string='القضايا', auto_join=True)
    consulting_ids = fields.One2many('consulting.consulting', 'project_id', string='الاستشارات', auto_join=True)
    contractconsulting_ids = fields.One2many('contractconsulting.contractconsulting', 'project_id', string='استشارات العقود', auto_join=True)
    project_type = fields.Selection([
            ('قضية', 'قضية'),
            ('استشارة', 'استشارة'),
            ('عقود', 'عقود'),
            ('اخرى', 'اخرى')
            ], string='نوع المشروع', store=True, copy=False, readonly=False)
    allowed_internal_user_ids = fields.Many2many('res.users', 'allowed_internal_user_ids', string="المسؤوليين والمساعدون", domain=[('share', '=', False)], compute='_allowed_internal_user_ids', store=True, readonly=False)
    
    allowed_internal_user_ids = fields.Many2many('res.users', 'allowed_internal_user_ids', string="المسؤوليين والمساعدون", domain=[('share', '=', False)], compute='_allowed_internal_user_ids', store=True, readonly=False)
    
    partner_id = fields.Many2one('res.partner',store=True)

    user_id = fields.Many2one('res.users', store=True)

    @api.depends('user_id','user_id.lawyer_assistants','user_id.lawyer_manager') 
    def _allowed_internal_user_ids(self):
        for project in self:
            if project.user_id.lawyer_manager:
                project.allowed_internal_user_ids = project.user_id + project.user_id.lawyer_assistants + project.user_id.lawyer_manager
            else:
                project.allowed_internal_user_ids = project.user_id + project.user_id.lawyer_assistants

            
    helper_ids = fields.Many2many('res.users', 'helper_ids', string="المساعدون", compute='_helper_ids', store=True)
    
    @api.depends('user_id','user_id.lawyer_assistants','user_id','allowed_internal_user_ids','user_id.lawyer_manager') 
    def _helper_ids(self):
        for project in self:
            if project.user_id.lawyer_manager:
                project.helper_ids = project.user_id.lawyer_assistants + project.allowed_internal_user_ids + project.user_id.lawyer_manager - project.user_id
            else:
                project.helper_ids = project.user_id.lawyer_assistants + project.allowed_internal_user_ids - project.user_id


    privacy_visibility = fields.Selection(default='followers')

class Task(models.Model):
    _inherit = "project.task"
    
    
    task_type = fields.Selection([
            ('مشروع', 'مشروع'),
            ('قضية', 'قضية'),
            ('استشارة', 'استشارة'),
            ('استشارة عقد', 'استشارة عقد'),
            ('تقرير جلسة', 'تقرير جلسة'),
            ], string='المهمة تابعة إلى', store=True, copy=False, readonly=False)
    litigation_id = fields.Many2one('litigation.litigation', string='القضية', auto_join=True)
    consulting_id = fields.Many2one('consulting.consulting', string='الاستشارة', auto_join=True)
    contractconsulting_id = fields.Many2one('contractconsulting.contractconsulting', string='استشارة العقد', auto_join=True)
    report_id = fields.Many2one('litigation.report', string='تقرير الجلسة', auto_join=True)
    state_id = fields.Selection([
            ('جديدة', 'جديدة'),
            ('قيد التنفيذ', 'قيد التنفيذ'),
            ('منتهية', 'منتهية'),
            ], string='حالة المهمة', default='جديدة', store=True, readonly=False, required=True, tracking=True)
    is_closed = fields.Boolean('مرحلة الإنتهاء', store=True, readonly=False, compute='check_value')
    date_deadline = fields.Date(string='الموعد النهائي', index=True, copy=False, tracking=True, required=True, readonly=False, default=date.today())
    following_to = fields.Char(compute='_following_to',string='تابعة إلى')
    allowed_users_task = fields.Many2many('res.users', 'allowed_users_task', string="الرؤية", compute='_allowed_users_task', store=True)
    
    @api.depends('project_id.allowed_internal_user_ids','project_id','litigation_id','consulting_id','contractconsulting_id','report_id') 
    def _allowed_users_task(self):
        for task in self:
            if task.litigation_id:
                task.allowed_users_task = task.litigation_id.project_id.allowed_internal_user_ids
            elif task.consulting_id:
                task.allowed_users_task = task.consulting_id.project_id.allowed_internal_user_ids
            elif task.contractconsulting_id:
                task.allowed_users_task = task.contractconsulting_id.project_id.allowed_internal_user_ids
            elif task.report_id:
                task.allowed_users_task = task.report_id.litigation_id.project_id.allowed_internal_user_ids
            elif task.project_id:
                task.allowed_users_task = task.project_id.allowed_internal_user_ids
            else:
                task.allowed_users_task = task.user_ids

                
    def _following_to(self):
        for task in self:
            if task.litigation_id:
                task.following_to = ("قضية: " + task.litigation_id.name)
            elif task.consulting_id:
                task.following_to = ("استشارة: " + task.consulting_id.name)
            elif task.contractconsulting_id:
                task.following_to = ("عقد: " + task.contractconsulting_id.name)
            elif task.report_id:
                task.following_to = ("قضية: " + task.report_id.litigation_id.name + " في جلسة: " + task.report_id.name)
            elif task.project_id:
                task.following_to = ("مشروع: " + task.project_id.name)
            else:
                task.following_to = ("لا شيء")

    
    @api.depends('state_id') 
    def _get_default_color(self):
        dateTimeDifference = 0
        dateTimeDifferenceInHours = 0
        for task in self:
            if task.state_id == 'جديدة':
                task.state_colors = 7
            elif task.state_id == 'قيد التنفيذ':
                task.state_colors = 7
            else:
                task.state_colors = 0

    state_colors = fields.Integer(string='Color', compute='_get_default_color', store=True)
    
    @api.depends('state_id') 
    def check_value(self): 
        for task in self:
            if task.state_id == 'منتهية': 
                task.is_closed = True 
            else:
                task.is_closed = False
                
    state_end_date = fields.Datetime(string="أنتهت في", store=True, tracking=True)
    state_start_date = fields.Datetime(string="بدأت في", store=True, tracking=True)
    
    @api.onchange('state_id') 
    def _get_state_end_date(self):
        for task in self:
            if task.state_id == 'منتهية':
                Today = fields.datetime.now()
                task.state_end_date = Today
          
    @api.onchange('state_id') 
    def _get_state_start_date(self):
        for task in self:
            if task.state_id == 'قيد التنفيذ':
                Today = fields.datetime.now()
                task.state_start_date = Today
                
    def check_updation(self):
        records=self.env['project.task'].sudo().search([('state_id','!=','منتهية')])
        for record in records:
            today = date.today()
            for user in record.user_ids:
                leave = self.env['hr.leave'].sudo().search([('request_date_from', '<=', today),
                                                     ('request_date_to', '>=', today),
                                                     ('employee_id', '=', user.employee_id.id),
                                                     ('state','=','validate')])
                if len(leave):
                    return
                else:
                    dateTimeDifference=datetime.now()-record.write_date
                    dateTimeDifferenceInHours = float(dateTimeDifference.total_seconds() / 3600)
                    if dateTimeDifferenceInHours >168:
                            base_url = self.company_id.website
                            url = base_url + '/web#id=%d&model=project.task&view_type=form' % (record.id)
                            body_html = ("لا يوجد أي حركة في مهمة: " + record.name + '<div>.</div>' + '<a href="%s"style="padding: 8px 16px 8px 16px; border-radius: 3px; background-color:#875A7B; text-align:center; text-decoration:none; color: #FFFFFF;">للإطلاع</a>' % url)
                            vals = {
                                'subject': "لا يوجد أي حركة في المهمة خلال الأسبوع هذا",
                                'body_html': body_html,
                                'author_id': record.user_id.partner_id.id,
                                'email_from': record.user_id.company_id.partner_id.email_formatted or record.user_id.email_formatted,
                                'email_to':record.user_id.partner_id.email,
                                'auto_delete': True,
                                'state': 'outgoing'
                            }
                            self.env['mail.mail'].sudo().create(vals).send()
                
    change_deadline = fields.Char(compute='_change_deadline')
    
    @api.onchange('timesheet_ids') 
    def _change_deadline(self):
        if self.date_deadline != False:
            if self.timesheet_ids:
                for time in self.timesheet_ids:
                    if time.date == datetime.today().date():
                        self.change_deadline = 'True'
                        self.state_id = 'قيد التنفيذ'
                    else:
                        self.change_deadline = 'False'
            else:
                self.change_deadline = 'False'
        else:
            self.change_deadline = 'True'
                 
                
    def _cron_deadline_reminder(self):
        for task in self.env['project.task'].search([('date_deadline', '!=', None),('user_id', '!=', None),('state_id','!=','منتهية')]):
            reminder_date = task.date_deadline - timedelta(days = 1)
            today = datetime.now().date()
            if reminder_date == today and task:
                base_url = task.company_id.website
                url = base_url + '/web#id=%d&model=project.task&view_type=form' % (task.id)
                body_html = ("للتذكير غدا هو الموعد النهائي لمهمة " + task.name + " يرجى منكم مراجعتها وإنهاءها "  + '<div>.</div>' + '<a href="%s"style="padding: 8px 16px 8px 16px; border-radius: 3px; background-color:#875A7B; text-align:center; text-decoration:none; color: #FFFFFF;">للإطلاع</a>' % url)
                subject = ("غدا هو الموعد النهائي لمهمة: " + task.name)
                vals = {
                    'subject': subject,
                    'body_html': body_html,
                    'author_id': task.user_id.partner_id.id,
                    'email_from': task.user_id.company_id.partner_id.email_formatted or task.user_id.email_formatted,
                    'email_to':task.user_id.partner_id.email,
                    'auto_delete': True,
                    'state': 'outgoing'
                }
                self.env['mail.mail'].sudo().create(vals).send()
        return True
                
                
# litigation information        
                
    litigation_partner = fields.Many2one(related='litigation_id.partner_id')
    consulting_partner = fields.Many2one(related='consulting_id.partner_id')
    contractconsulting_partner = fields.Many2one(related='contractconsulting_id.partner_id')
                
class litigation(models.Model):
    _name = 'litigation.litigation'
    _description = 'القضايا'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = 'state desc'
    
    
    partner_id_emails = fields.Char(compute='get_partner_id_emails')

    def get_partner_id_emails(self):
        for litigation in self:
            full_permission_email = ''
            full_permission_emails = ''
            partner_email = ''
            for full_permission in litigation.partner_id.full_permission:
                full_permission_email += full_permission.partner_id.email + ','
            full_permission_emails += full_permission_email
            if litigation.partner_id.email:
                partner_email = litigation.partner_id.email
            full_emails = full_permission_emails + partner_email
            litigation.partner_id_emails = full_emails

    
    
    portal_url = fields.Char(compute='get_portal_url')
    
    def get_portal_url(self):
        base_url = self.company_id.website
        self.portal_url = base_url + '/my/litigation/' + str(self.id) + '?access_token=' + str(self.access_token)

    
    url = fields.Char(compute='get_url')
    
    def get_url(self):
        base_url = self.company_id.website
        self.url = base_url + '/web#id=' + str(self.id) + '&model=litigation.litigation&view_type=form'

    def get_portal_url_pdf_download(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        self.ensure_one()
        base_url = self.company_id.website
        access_url = base_url + '/my/litigation_print/' + str(self.id)
        url = access_url + '%s?access_token=%s%s%s%s%s' % (
            suffix if suffix else '',
            self.access_token,
            '&report_type=%s' % report_type if report_type else '',
            '&download=true' if download else '',
            query_string if query_string else '',
            '#%s' % anchor if anchor else ''
        )
        return url

    def _get_report_base_filename(self):
        self.ensure_one()
        if self.litigation_number:
            return '%s' % (self.litigation_number)
        else:
            return '%s' % (self.name)

    def preview_portal(self):
        self.ensure_one()
        base_url = self.company_id.website
        portal_url = base_url + '/my/litigation/' + str(self.id) + '?access_token=' + str(self.access_token)
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': portal_url,
        }    
    
    def _default_access_token(self):
        return str(uuid.uuid4())

    access_token = fields.Char('Security Token', required=True, default=_default_access_token, readonly=True)
                
    def attachment_tree_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        action['domain'] = str([('res_model', '=', 'litigation.litigation'),('res_id', 'in', self.ids),])
        action['context'] = "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        return action
    
    def _compute_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'litigation.litigation'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = { res['res_id']: res['res_id_count'] for res in read_group_res }
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)
    
    
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_confirm(self):
        self.write({'state': 'confirm'})
        notification_ids = []
        for litigation in self:
            if litigation.lawyer_manager.user_id.id:
                notification_ids.append((0,0,{
                'res_partner_id':litigation.lawyer_manager.user_id.partner_id.id,
                'notification_type':'inbox'}))
            litigation.message_post(
                subject="اعتماد",
                body= "تم تقديم طلب الاعتماد، نأمل منكم الإطلاع والتعميد",
                message_type='notification',
                notification_ids=notification_ids,
               )
        if litigation.user_id:
            litigation.message_subscribe(partner_ids=litigation.user_id.partner_id.ids)
        if litigation.partner_id:
            litigation.message_subscribe(partner_ids=litigation.partner_id.ids)
        if litigation.parent_id:
            litigation.message_subscribe(partner_ids=litigation.parent_id.ids)
        return True

    def action_refuse(self):
        self.write({'state': 'Refuse'})
        notification_ids = []
        for litigation in self:
            if litigation.lawyer_manager.user_id.id:
                notification_ids.append((0,0,{
                'res_partner_id':litigation.user_id.partner_id.id,
                'notification_type':'inbox'}))
            litigation.message_post(
                subject="رفض",
                body= "تم إعادة القضية. نأمل منكم مراجعتها وإعادة تقديم طلب الاعتماد",
                message_type='notification',
                notification_ids=notification_ids,
               )
        return True

    def action_suspended(self):
        self.write({'state': 'suspended'})
        return True
    
    def action_pull(self):
        self.write({'state': 'confirm'})
        return True

    def action_approve(self):
        self.write({'state': 'Approve'})
        notification_ids = []
        for litigation in self:
            if litigation.lawyer_manager.user_id.id:
                if self.env.user.id != litigation.lawyer_manager.user_id.id:
                    notification_ids.append((0,0,{
                    'res_partner_id':litigation.lawyer_manager.user_id.partner_id.id,
                    'notification_type':'inbox'}))
                litigation.message_post(
                    subject="موافقة",
                    body= ("تمت الموافقة على القضية من قبل " + self.env.user.name),
                    message_type='notification',
                    notification_ids=notification_ids,
                   )
            if litigation.next_court_date and litigation.lawyer_manager.user_id.id:
                meeting_values = {
                    'name': self.name,
                    'user_id': self.user_id.id,
                    'start': self.next_court_date,
                    'stop': self.next_court_date,
                    'allday': False,
                    'privacy': 'confidential',
                    'activity_ids': [(5, 0, 0)],
                    'partner_ids': [(6, 0, [litigation.lawyer_manager.user_id.partner_id.id,
                                            litigation.user_id.partner_id.id, litigation.partner_id.id])],
                }
                self.env['calendar.event'].with_context(no_mail_to_attendees=True, active_model=self._name).create(meeting_values)
            if litigation.partner_id_emails:
                mail_template = self.env.ref('litigation.send_litigation_partner')
                mail_template.send_mail(self.id, force_send=True,notif_layout='mail.mail_notification_light')
        return True

    def action_close(self):
        self.write({'state': 'close'})
        return True
    
    
    system_user = fields.Char(compute='_get_system_user')
    
    def _get_system_user(self):
        for litigation in self:
            if litigation.env.user.has_group('base.group_system'):
                litigation.system_user = 'True'
            else:
                litigation.system_user = 'False'

    current_user = fields.Char(compute='_get_current_user')
    
    def _get_current_user(self):
        for litigation in self:
            if litigation.env.user.id == litigation.user_id.id:
                if litigation.user_id.lawyer_manager:
                    litigation.current_user = 'False'
                else:
                    litigation.current_user = 'True'
            elif litigation.env.user.has_group('litigation.group_law_lawyer_manager'):
                litigation.current_user = 'True'
            elif litigation.env.user.id == litigation.user_id.lawyer_manager.id:
                litigation.current_user = 'True'
            else:
                litigation.current_user = 'False'
                
    @api.depends('partner_id')
    def _compute_attorney_id(self):
        for litigation in self:
            if litigation.partner_id:
                attorney_id = self.env['attorney.attorney'].sudo().search([('partner_id','=', litigation.partner_id.id),('expiration','!=','منتهية')], limit=1)
                if attorney_id:
                    litigation.attorney_id = attorney_id
                else:
                    litigation.attorney_id = False
                    
    lawyer_manager = fields.Many2one('res.users', string='المدير المحامي', compute='_get_lawyer_manager')

    def _get_lawyer_manager(self):
        for litigation in self:
            lawyer_manager = litigation.user_id.id
            if litigation.user_id.lawyer_manager:
                lawyer_manager = litigation.user_id.lawyer_manager
            litigation.lawyer_manager = lawyer_manager
            
            
    @api.depends('project_id.partner_id','project_id.user_id')
    def _get_partner_user(self):
        for litigation in self:
            partner_id = False
            user_id = self.env.user.id
            if litigation.project_id.partner_id:
                partner_id = litigation.project_id.partner_id.id
            if litigation.project_id.user_id:
                user_id = litigation.project_id.user_id.id
            litigation.partner_id = partner_id
            litigation.user_id = user_id

    next_court_date = fields.Datetime(string='موعد الجلسة القادمة', compute='_get_next_court_date' , store=True)

    @api.depends('report_ids','report_ids.next_court_date')
    def _get_next_court_date(self):
        for litigation in self:
            next_court_date = False
            if litigation.next_court_date:
                next_court_date = litigation.next_court_date
            last_report = self.env['litigation.report'].search([('litigation_id','=',litigation.id)], order='court_date desc', limit=1)
            if last_report.next_court_date:
                next_court_date = last_report.next_court_date
            litigation.next_court_date = next_court_date


    name = fields.Char("القضية", tracking=True)
    success_possibility = fields.Selection([
        ('0', 'غير محدد'),
        ('1', 'ضعيفة'),
        ('2', 'متوسطة'),
        ('3', 'عالية'),
        ], default='0', index=True, string="احتمالية النجاح")
    project_id = fields.Many2one('project.project', string='المشروع', store=True, readonly=False, index=True, change_default=True)
    partner_id = fields.Many2one('res.partner', compute='_get_partner_user', string='العميل', tracking=True, store=True)
    attorney_id = fields.Many2one('attorney.attorney', string='الوكالة', compute='_compute_attorney_id', readonly=False, store=True)
    parent_id = fields.Many2one('res.partner', related='partner_id.parent_id', string='شركة العميل', auto_join=True)
    full_permission = fields.Many2many(related='partner_id.full_permission')
    manager_permission = fields.Many2many(related='partner_id.manager_permission')
    company_id = fields.Many2one('res.company', related='user_id.company_id', string='Company', required=True)
    user_id = fields.Many2one('res.users', compute='_get_partner_user', string='المحامي', tracking=True, store=True)
    helper = fields.Boolean(string='القضية تحتاج مساعد')
    helper_ids = fields.Many2many(related='project_id.helper_ids', string='مساعد المحامي')
    establishment_date = fields.Date(string='تاريخ القيد', index=True, tracking=True)
    caliming_date = fields.Date(string='تاريخ الاستحقاق', index=True, tracking=True)
    appeal_date = fields.Date(string='تاريخ الاستئناف', index=True, tracking=True)
    litigation_number = fields.Char(string='رقم القضية', index=True, tracking=True)
    appeal_number = fields.Char(string='رقم القضية بالاستئناف', index=True, tracking=True)
    opponent_according = fields.Char(string='بموجب الخصم', index=True, tracking=True)
    client_according = fields.Char(string='بموجب الموكل', index=True, tracking=True)
    client_representative = fields.Many2one('res.partner', string='ممثل الموكل', index=True, tracking=True)
    opponent = fields.Many2one('res.partner', string='الخصم', auto_join=True, tracking=True)
    circuit = fields.Char(string='الدائرة القضائية', index=True, tracking=True)
    appeal_circuit = fields.Char(string='الدائرة القضائية بالاستئناف', index=True, tracking=True)
    case_amount = fields.Monetary(string='مبلغ محل الدعوى', currency_field='company_currency', store=True, tracking=True)
    company_currency = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id', readonly=True)
    opponent_representative = fields.Char(string='ممثل الخصم', index=True, tracking=True)
    summary = fields.Text(string='موضوع الدعوى', tracking=True)
    requests_ids = fields.One2many('litigation.requests', 'litigation_id', string='طلبات الدعوى')
    arguments_ids = fields.One2many('litigation.arguments', 'litigation_id', string='أسانيد الدعوى')
    notes_ids = fields.One2many('litigation.notes', 'litigation_id', string='مذكرات الدعوى')
    report_ids = fields.One2many('litigation.report', 'litigation_id', string='تقرير القضية')
    task_ids = fields.One2many('project.task', 'litigation_id', string='المهام')
    other = fields.Char(string='اخرى', index=True, tracking=True)
    attachment_number = fields.Integer(compute='_compute_attachment_number', string="Number of Attachments")
    file = fields.Binary(string='ملف الحكم')
    judgment = fields.Text(string='الحكم', tracking=True)
    case_type = fields.Selection([
            ('أحوال شخصية', 'أحوال شخصية'),
            ('تنفيذ', 'تنفيذ'),
            ('جزائية', 'جزائية'),
            ('عامة', 'عامة'),
            ('عمالية', 'عمالية'),
            ('إدارية', 'إدارية'),
            ('تجارية', 'تجارية'),
            ('اخرى', 'اخرى')
            ], string='نوع الدعوى', store=True, copy=False, readonly=False, tracking=True)
    personal_status = fields.Selection([
            ('دعوى إثبات رضاع أو مصاهرة', 'دعوى إثبات رضاع أو مصاهرة'),
            ('دعوى إقامة حارس قضائي', 'دعوى إقامة حارس قضائي'),
            ('دعوى تعويض', 'دعوى تعويض'),
            ('دعوى مطالبة بأتعاب محامين أو وكلاء', 'دعوى مطالبة بأتعاب محامين أو وكلاء'),
            ('دعوى مطالبة بمستندات', 'دعوى مطالبة بمستندات'),
            ('دعوى معارضة على صك إنهائي', 'دعوى معارضة على صك إنهائي'),
            ('دعوى منع من السفر', 'دعوى منع من السفر'),
            ('دعوى هبة أو رجوع عنها', 'دعوى هبة أو رجوع عنها'),
            ('الانهاءات', 'الانهاءات'),
            ('دعوى إبطال وقف أو وصية', 'دعوى إبطال وقف أو وصية'),
            ('دعوى اثبات وقف أو وصية', 'دعوى اثبات وقف أو وصية'),
            ('دعوى استحقاق في وقف أو وصية', 'دعوى استحقاق في وقف أو وصية'),
            ('دعوى عزل ناظر وقف أو وصية', 'دعوى عزل ناظر وقف أو وصية'),
            ('دعوى محاسبة ناظر وقف أو وصية', 'دعوى محاسبة ناظر وقف أو وصية'),
            ('دعوى إنهاء وقف أو وصية', 'دعوى إنهاء وقف أو وصية'),
            ('أجرة رضاع أو حضانة', 'أجرة رضاع أو حضانة'),
            ('دعوى تسليم صغير لحاضنه', 'دعوى تسليم صغير لحاضنه'),
            ('دعوى حضانة', 'دعوى حضانة'),
            ('دعوى رؤية صغير', 'دعوى رؤية صغير'),
            ('زيادة نفقة أو إنقاصها أو إلغائها', 'زيادة نفقة أو إنقاصها أو إلغائها'),
            ('دعوى زيارة أولاد أو غيرهم', 'دعوى زيارة أولاد أو غيرهم'),
            ('دعوى نفقة', 'دعوى نفقة'),
            ('دعوى إثبات رجعة', 'دعوى إثبات رجعة'),
            ('دعوى إثبات طلاق', 'دعوى إثبات طلاق'),
            ('دعوى إثبات نكاح', 'دعوى إثبات نكاح'),
            ('دعوى خلع', 'دعوى خلع'),
            ('دعوى صداق', 'دعوى صداق'),
            ('دعوى عفش الزوجية', 'دعوى عفش الزوجية'),
            ('فسخ نكاح', 'فسخ نكاح'),
            ('دعوى إثبات نسب أو نفيه', 'دعوى إثبات نسب أو نفيه'),
            ('دعوى إذن سفر', 'دعوى إذن سفر'),
            ('دعوى حجر أو رفعه', 'دعوى حجر أو رفعه'),
            ('دعوى عزل ولي', 'دعوى عزل ولي'),
            ('دعوى عضل', 'دعوى عضل'),
            ('دعوى محاسبة ولي', 'دعوى محاسبة ولي'),
            ('دعوى قسمة تركة أكثر من 50 مليون ريال', 'دعوى قسمة تركة أكثر من 50 مليون ريال'),
            ('دعوى قسمة تركة عقارية', 'دعوى قسمة تركة عقارية'),
            ('دعوى قسمة تركة مالية', 'دعوى قسمة تركة مالية'),
            ('دعوى محاسبة وكيل أو وارث', 'دعوى محاسبة وكيل أو وارث'),
            ('دعوى مطالبة بأجرة سكن', 'دعوى مطالبة بأجرة سكن'),
            ], string='أحوال شخصية', store=True, copy=False, readonly=False, tracking=True)
    execute = fields.Selection([
            ('الامتناع عن قبول السند', 'الامتناع عن قبول السند'),
            ('دعوى الإعسار', 'دعوى الإعسار'),
            ('دعوى الملاءة', 'دعوى الملاءة'),
            ('عدم توفر شرط شكلي للسند أو تزويره أو إنكار التوقيع', 'عدم توفر شرط شكلي للسند أو تزويره أو إنكار التوقيع'),
            ('عدم الصفة', 'عدم الصفة'),
            ('الإبراء بعد صدور السند التنفيذي', 'الإبراء بعد صدور السند التنفيذي'),
            ('التأجيل بعد صدور السند التنفيذي', 'التأجيل بعد صدور السند التنفيذي'),
            ('الحوالة بعد صدور السند التنفيذي', 'الحوالة بعد صدور السند التنفيذي'),
            ('الصلح بعد صدور السند التنفيذي', 'الصلح بعد صدور السند التنفيذي'),
            ('المال المحجوز يفوق مقدار الدين المطالب به', 'المال المحجوز يفوق مقدار الدين المطالب به'),
            ('المقاصة بموجب سند تنفيذي', 'المقاصة بموجب سند تنفيذي'),
            ('الوفاء بعد صدور السند التنفيذي', 'الوفاء بعد صدور السند التنفيذي'),
            ('امتناع شاغل العقار عن الإخلاء لحمه سند تنفيذي', 'امتناع شاغل العقار عن الإخلاء لحمه سند تنفيذي'),
            ('تواطؤ أثناء المزاد أو التأثير على سعر المزاد', 'تواطؤ أثناء المزاد أو التأثير على سعر المزاد'),
            ('رد ما استوفي خطأ', 'رد ما استوفي خطأ'),
            ('صحة تقرير المحجوز لديه بما في ذمته', 'صحة تقرير المحجوز لديه بما في ذمته'),
            ('عيب في العين المباعة', 'عيب في العين المباعة'),
            ('دعوى التعويض', 'دعوى التعويض'),
            ('المنازعة في أجرة الحارس القضائي أو محاسبته أو استبداله', 'المنازعة في أجرة الحارس القضائي أو محاسبته أو استبداله'),
            ], string='تنفيذ', store=True, copy=False, readonly=False, tracking=True)
    penal = fields.Selection([
            ('منع من السفر', 'منع من السفر'),
            ('إثبات تنازل', 'إثبات تنازل'),
            ('تسليم مضبوطات', 'تسليم مضبوطات'),
            ('الحراسة القضائية', 'الحراسة القضائية'),
            ('الحجز التحفظي', 'الحجز التحفظي'),
            ('استيثاق لإثبات الحالة أو شهادة يخشى فواتها', 'استيثاق لإثبات الحالة أو شهادة يخشى فواتها'),
            ('وقف الأعمال الجديدة', 'وقف الأعمال الجديدة'),
            ('سحر أو كهانة أو شعوذة', 'سحر أو كهانة أو شعوذة'),
            ('تشهير أو تشويه سمعة', 'تشهير أو تشويه سمعة'),
            ('إطلاق نار', 'إطلاق نار'),
            ('ابتزاز', 'ابتزاز'),
            ('تزوير', 'تزوير'),
            ('مخالفة النظام الجزائي لجرائم التزوير', 'مخالفة النظام الجزائي لجرائم التزوير'),
            ('التحرش', 'التحرش'),
            ('انتحال شخصية الغير', 'انتحال شخصية الغير'),
            ('انتهاك حرمة مكان', 'انتهاك حرمة مكان'),
            ('تحريض', 'تحريض'),
            ('تخبيب', 'تخبيب'),
            ('تنظيم بيع سندات الهدي والأضاحي على الحجاج', 'تنظيم بيع سندات الهدي والأضاحي على الحجاج'),
            ('خطف', 'خطف'),
            ('خيانة الأمانة', 'خيانة الأمانة'),
            ('شكوى أو دعوى كيدية', 'شكوى أو دعوى كيدية'),
            ('سب أو شتم', 'سب أو شتم'),
            ('شهادة زور', 'شهادة زور'),
            ('عقوق الوالدين', 'عقوق الوالدين'),
            ('قتل', 'قتل'),
            ('مضاربة أو اعتداء جسدي', 'مضاربة أو اعتداء جسدي'),
            ('نصب أو احتيال', 'نصب أو احتيال'),
            ('التستر على جريمة أو مجرم', 'التستر على جريمة أو مجرم'),
            ('نظام الحماية من الإيذاء', 'نظام الحماية من الإيذاء'),
            ('الجرائم المعلوماتية', 'الجرائم المعلوماتية'),
            ('جرائم العرض', 'جرائم العرض'),
            ('تهديد', 'تهديد'),
            ('قذف', 'قذف'),
            ('سرقة', 'سرقة'),
            ('مادون النفس', 'مادون النفس'),
            ('نفس', 'نفس'),
            ('أتعاب المحاماة أو الوكلاء', 'أتعاب المحاماة أو الوكلاء'),
            ('أرش', 'أرش'),
            ('تعويض', 'تعويض'),
            ('دية', 'دية'),
            ('رد العين', 'رد العين'),
            ('أضرار التقاضي', 'أضرار التقاضي'),
            ], string='جزائية', store=True, copy=False, readonly=False, tracking=True)
    general = fields.Selection([
            ('رد اعتبار (إثبات الاستقامة بعد السابقة الجنائية)', 'رد اعتبار (إثبات الاستقامة بعد السابقة الجنائية)'),
            ('إثبات عدم تملك مسكن/بيت', 'إثبات عدم تملك مسكن/بيت'),
            ('استيثاق لإثبات الحال أو شهادة يخشى فواتها في غير خصومة', 'استيثاق لإثبات الحال أو شهادة يخشى فواتها في غير خصومة'),
            ('تنازل عن أرش إصابة أو دية (غير العمد و شبه العمد)', 'تنازل عن أرش إصابة أو دية (غير العمد و شبه العمد)'),
            ('إنهاء عام', 'إنهاء عام'),
            ('حراسة قضائية', 'حراسة قضائية'),
            ('منع من السفر', 'منع من السفر'),
            ('وقف الأعمال الجديدة', 'وقف الأعمال الجديدة'),
            ('أجرة الأجير اليومية أو الأسبوعية', 'أجرة الأجير اليومية أو الأسبوعية'),
            ('استرداد حيازة العقار', 'استرداد حيازة العقار'),
            ('استيثاق لإثبات الحالة أو شهادة يخشى فواتها', 'استيثاق لإثبات الحالة أو شهادة يخشى فواتها'),
            ('منع التعرض للحيازة', 'منع التعرض للحيازة'),
            ('حجز تحفظي', 'حجز تحفظي'),
            ('إخلاء عقار', 'إخلاء عقار'),
            ('استطراق', 'استطراق'),
            ('تداخل العقارات', 'تداخل العقارات'),
            ('حق الشفعة', 'حق الشفعة'),
            ('ملكية عقار', 'ملكية عقار'),
            ('رفع اليد ضد جهة حكومية', 'رفع اليد ضد جهة حكومية'),
            ('قسمة عقارات مشتركة', 'قسمة عقارات مشتركة'),
            ('مساهمة عقارية', 'مساهمة عقارية'),
            ('مساييل أو حمى', 'مساييل أو حمى'),
            ('مقاولات إنشاء المباني', 'مقاولات إنشاء المباني'),
            ('إثبات رهن أو بيع المرهون', 'إثبات رهن أو بيع المرهون'),
            ('رد مسروق', 'رد مسروق'),
            ('عارية', 'عارية'),
            ('قرض أو سلف', 'قرض أو سلف'),
            ('هبة في غير عقار', 'هبة في غير عقار'),
            ('أتعاب المحاماة', 'أتعاب المحاماة'),
            ('أجرة أعمال', 'أجرة أعمال'),
            ('أجرة عقار', 'أجرة عقار'),
            ('أجرة عين (منقول)', 'أجرة عين (منقول)'),
            ('أرش إصابة غير مرورية', 'أرش إصابة غير مرورية'),
            ('التعويض عن أضرار التقاضي', 'التعويض عن أضرار التقاضي'),
            ('ثمن مبيع', 'ثمن مبيع'),
            ('دعوى حوالة', 'دعوى حوالة'),
            ('شراكة في أملاك غير عقارية', 'شراكة في أملاك غير عقارية'),
            ('ضمان كفالة', 'ضمان كفالة'),
            ('محاسبة', 'محاسبة'),
            ('مطالبة الضامن للمضمون عنه (كفيل لمكفوله)', 'مطالبة الضامن للمضمون عنه (كفيل لمكفوله)'),
            ('مطالبة بدية أو إرش في غير حادث مروري', 'مطالبة أو إرش بدية في غير حادث مروري'),
            ('وديعة', 'وديعة'),
            ('حق خاص ناشئ عن حادث مروري', 'حق خاص ناشئ عن حادث مروري'),
            ('إثبات عقد', 'إثبات عقد'),
            ('رفع ضرر أو التعويض عنه', 'رفع ضرر أو التعويض عنه'),
            ('رد العين', 'رد العين'),
            ('عقد استصناع', 'عقد استصناع'),
            ('فسخ عقد أو بطلانه', 'فسخ عقد أو بطلانه'),
            ('قسمة منافع (مهايأة)', 'قسمة منافع (مهايأة)'),
            ('مطالبة بمستندات', 'مطالبة بمستندات'),
            ('التحكيم', 'التحكيم')
            ], string='عامة', store=True, copy=False, readonly=False, tracking=True)    
    managerial = fields.Selection([
            ('قرار', 'قرار'),
            ('تعويض', 'تعويض'),
            ('عقد', 'عقد'),
            ('منازعة إدارية أخرى', 'منازعة إدارية أخرى'),
            ('حقوق وظيفية', 'حقوق وظيفية'),
            ('تأديب', 'تأديب'),
            ('تقاعد', 'تقاعد'),
            ('طلبات قضائية', 'طلبات قضائية'),
            ('غرامات', 'غرامات'),
            ('طلبات أوامر الحجز', 'طلبات أوامر الحجز'),
            ('طلبات تنفيذ مقدمة من جهة إدارية', 'طلبات تنفيذ مقدمة من جهة إدارية'),
            ], string='إدارية', store=True, copy=False, readonly=False)
    managerial_1 = fields.Selection([
            ('نزع ملكية', 'نزع ملكية'),
            ('تراخيص', 'تراخيص'),
            ('ملكية فكرية', 'ملكية فكرية'),
            ('تجارة وصناعة', 'تجارة وصناعة'),
            ('صحية', 'صحية'),
            ('انتخابات', 'انتخابات'),
            ('أجانب', 'أجانب'),
            ('عقار', 'عقار'),
            ('مالية', 'مالية'),
            ('خدمة مدنية', 'خدمة مدنية'),
            ('خدمة عسكرية', 'خدمة عسكرية'),
            ('تعليمية', 'تعليمية'),
            ('وظائف خاصة', 'وظائف خاصة'),
            ('جمعيات النفع العام', 'جمعيات النفع العام'),
            ('أحوال مدنية', 'أحوال مدنية'),
            ('تخطيط عمراني', 'تخطيط عمراني'),
            ('تدابير مؤقتة', 'تدابير مؤقتة'),
            ('خدمات عامة', 'خدمات عامة'),
            ('الضبطية الجنائية', 'الضبطية الجنائية'),
            ('اتصالات', 'اتصالات'),
            ], string='قرار', store=True, copy=False, readonly=False)
    expropriation = fields.Many2one('expropriation.type', string='نزع ملكية', auto_join=True)
    licenses = fields.Selection([
            ('اتصالات وتقنية معلومات', 'اتصالات وتقنية معلومات'),
            ('استثمار', 'استثمار'),
            ('أمنية', 'أمنية'),
            ('بلدية', 'بلدية'),
            ('تعدين', 'تعدين'),
            ('تعليمية', 'تعليمية'),
            ('حج وعمرة', 'حج وعمرة'),
            ('زراعية', 'زراعية'),
            ('صناعية', 'صناعية'),
            ('سياحية', 'سياحية'),
            ('محطات وقود', 'محطات وقود'),
            ('محلات تجارية', 'محلات تجارية'),
            ('مهنية', 'مهنية'),
            ('منشآت ومنتجات صحية', 'منشآت ومنتجات صحية'),
            ('نقل', 'نقل'),
            ('خدمات بريدية', 'خدمات بريدية'),
            ('ثقافية وإعلامية', 'ثقافية وإعلامية'),
            ], string='تراخيص', store=True, copy=False, readonly=False)
    licenses_1 = fields.Selection([
            ('منح', 'منح'),
            ('تجديد', 'تجديد'),
            ('سحب', 'سحب'),
            ('شطب', 'شطب'),
            ('إيقاف', 'إيقاف'),
            ('إلغاء', 'إلغاء'),
            ], string='نوعها', store=True, copy=False, readonly=False)
    invention = fields.Many2one('invention.type', string='ملكية فكرية', auto_join=True)
    trade = fields.Selection([
            ('وكالة تجارية', 'وكالة تجارية'),
            ('سجل تجاري', 'سجل تجاري'),
            ('شركات', 'شركات'),
            ('قرارات لجنة المساهمات العقارية', 'قرارات لجنة المساهمات العقارية'),
            ('مجلس الهيئات والغرف التجارية', 'مجلس الهيئات والغرف التجارية'),
            ('مدن صناعية', 'مدن صناعية'),
            ], string='التجارة والصناعة', store=True, copy=False, readonly=False)
    health = fields.Many2one('health.type', string='الصحية', auto_join=True)
    election = fields.Selection([
            ('قيد ناخب في البلدية', 'قيد ناخب في البلدية'),
            ('ترشيح ناخب في البلدية', 'ترشيح ناخب في البلدية'),
            ('استبعاد ناخب في البلدية', 'استبعاد ناخب في البلدية'),
            ('نتائج انتخابات في البلدية', 'نتائج انتخابات في البلدية'),
            ('قيد ناخب في جمعيات عمومية', 'قيد ناخب في جمعيات عمومية'),
            ('ترشيح ناخب في جمعيات عمومية', 'ترشيح ناخب في جمعيات عمومية'),
            ('استبعاد ناخب في جمعيات عمومية', 'استبعاد ناخب في جمعيات عمومية'),
            ('نتائج انتخابات في جمعيات عمومية', 'نتائج انتخابات في جمعيات عمومية'),
            ('قيد ناخب في مجالس', 'قيد ناخب في مجالس'),
            ('ترشيح ناخب في مجالس', 'ترشيح ناخب في مجالس'),
            ('استبعاد ناخب في مجالس', 'استبعاد ناخب في مجالس'),
            ('نتائج انتخابات في مجالس', 'نتائج انتخابات في مجالس'),
            ], string='انتخابات', store=True, copy=False, readonly=False)
    foregners = fields.Selection([
            ('ترحيل', 'ترحيل'),
            ('خدم المنازل', 'خدم المنازل'),
            ('رفض منح تأشيرة', 'رفض منح تأشيرة'),
            ('منع من السفر', 'منع من السفر'),
            ('إلغاء بلاغ', 'إلغاء بلاغ'),
            ('نقل كفالة', 'نقل كفالة'),
            ], string='أجانب', store=True, copy=False, readonly=False)
    estate = fields.Selection([
            ('تعديات', 'تعديات'),
            ('توثيق', 'توثيق'),
            ('منح أراضي', 'منح أراضي'),
            ('تخصيص أرض', 'تخصيص أرض'),
            ], string='عقار', store=True, copy=False, readonly=False)
    finance = fields.Selection([
            ('إعانات حكومية', 'إعانات حكومية'),
            ('إعانة كوارث طبيعية', 'إعانة كوارث طبيعية'),
            ('إيرادات الدولة', 'إيرادات الدولة'),
            ('رسوم حكومية', 'رسوم حكومية'),
            ('ضمان اجتماعي', 'ضمان اجتماعي'),
            ('لجان زكوية وضريبية', 'لجان زكوية وضريبية'),
            ('مصرفية', 'مصرفية'),
            ('طلب قرض حكومي', 'طلب قرض حكومي'),
            ], string='المالية', store=True, copy=False, readonly=False)
    civil_service = fields.Selection([
            ('إجازة', 'إجازة'),
            ('إخلاء طرف', 'إخلاء طرف'),
            ('استقالة', 'استقالة'),
            ('إعارة', 'إعارة'),
            ('إنهاء خدمة', 'إنهاء خدمة'),
            ('إيفاد وابتعاث', 'إيفاد وابتعاث'),
            ('تثبيت', 'تثبيت'),
            ('تحويل مسمى وظيفي', 'تحويل مسمى وظيفي'),
            ('تدريب', 'تدريب'),
            ('ترقية', 'ترقية'),
            ('تصنيف وظيفي', 'تصنيف وظيفي'),
            ('تعديل درجة وظيفية', 'تعديل درجة وظيفية'),
            ('تعيين', 'تعيين'),
            ('تقويم وظيفي', 'تقويم وظيفي'),
            ('تكليف', 'تكليف'),
            ('تمديد خدمة', 'تمديد خدمة'),
            ('حسم من الراتب', 'حسم من الراتب'),
            ('عدم اعتبار إصابة عمل', 'عدم اعتبار إصابة عمل'),
            ('قرارات أكاديمية', 'قرارات أكاديمية'),
            ('كف يد', 'كف يد'),
            ('ندب', 'ندب'),
            ('نقل', 'نقل'),
            ('احتساب إجازة', 'احتساب إجازة'),
            ], string='خدمة مدنية', store=True, copy=False, readonly=False)
    military_service = fields.Selection([
            ('ابتعاث', 'ابتعاث'),
            ('إخلاء طرف', 'إخلاء طرف'),
            ('استقالة', 'استقالة'),
            ('استيداع', 'استيداع'),
            ('إعارة', 'إعارة'),
            ('إلحاق', 'إلحاق'),
            ('إنهاء خدمة', 'إنهاء خدمة'),
            ('ترقية', 'ترقية'),
            ('تصنيف وظيفي', 'تصنيف وظيفي'),
            ('تقويم وظيفي', 'تقويم وظيفي'),
            ('حسم من الراتب', 'حسم من الراتب'),
            ('عدم اعتبار إصابة عمل', 'عدم اعتبار إصابة عمل'),
            ('منح أوسمة', 'منح أوسمة'),
            ('نقل', 'نقل'),
            ('تعيين', 'تعيين'),
            ], string='خدمة عسكرية', store=True, copy=False, readonly=False)
    educational = fields.Selection([
            ('استبعاد من الدراسة', 'استبعاد من الدراسة'),
            ('تعليم أهلي', 'تعليم أهلي'),
            ('حرمان من اختبار', 'حرمان من اختبار'),
            ('رسوم دراسية', 'رسوم دراسية'),
            ('قبول طالب', 'قبول طالب'),
            ('مجالس علمية', 'مجالس علمية'),
            ('معادلة مؤهلات', 'معادلة مؤهلات'),
            ('نتائج اختبارات', 'نتائج اختبارات'),
            ('نتيجة قياس', 'نتيجة قياس'),
            ('خفض نصاب', 'خفض نصاب'),
            ], string='تعليمية', store=True, copy=False, readonly=False)
    special_jobs = fields.Selection([
            ('رئيس مركز', 'رئيس مركز'),
            ('شيخ قبيلة', 'شيخ قبيلة'),
            ('عمدة', 'عمدة'),
            ('محافظ', 'محافظ'),
            ('معرف', 'معرف'),
            ], string='وظائف خاصة', store=True, copy=False, readonly=False)
    civil_status = fields.Selection([
            ('إضافة لقب', 'إضافة لقب'),
            ('تسجيل اسم', 'تسجيل اسم'),
            ('تعديل اسم أو تغييره', 'تعديل اسم أو تغييره'),
            ('تعديل تاريخ ميلاد', 'تعديل تاريخ ميلاد'),
            ('تعديل مكان ميلاد', 'تعديل مكان ميلاد'),
            ('تعديل مهنة', 'تعديل مهنة'),
            ('حذف لقب', 'حذف لقب'),
            ('سحب جنسية', 'سحب جنسية'),
            ('إصدار سجل أسرة', 'إصدار سجل أسرة'),
            ('إصدار شهادة ميلاد', 'إصدار شهادة ميلاد'),
            ('إصدار هوية وطنية', 'إصدار هوية وطنية'),
            ('منح جنسية', 'منح جنسية'),
            ], string='أحوال مدنية', store=True, copy=False, readonly=False)
    urban = fields.Selection([
            ('زوائد تنظيمية', 'زوائد تنظيمية'),
            ('زوائد تخطيطية', 'زوائد تخطيطية'),
            ('زوائد منح', 'زوائد منح'),
            ('اعتماد مخطط', 'اعتماد مخطط'),
            ('إعادة تنظيم مخطط', 'إعادة تنظيم مخطط'),
            ('تحويل شارع إلى تجاري', 'تحويل شارع إلى تجاري'),
            ('تحويل شارع إلى سكني', 'تحويل شارع إلى سكني'),
            ('تحويل مسار طريق', 'تحويل مسار طريق'),
            ('فتح شارع', 'فتح شارع'),
            ('إغلاق شارع', 'إغلاق شارع'),
            ('تغيير عرض شارع', 'تغيير عرض شارع'),
            ('إنشاء مرفق', 'إنشاء مرفق'),
            ('إلغاء مرفق', 'إلغاء مرفق'),
            ('نقل غرفة كهرباء', 'نقل غرفة كهرباء'),
            ('تغيير منسوب طريق', 'تغيير منسوب طريق'),
            ('رفع مساحي', 'رفع مساحي'),
            ('تغيير مسمى مكان', 'تغيير مسمى مكان'),
            ], string='تخطيط عمراني', store=True, copy=False, readonly=False)
    temp_measure = fields.Selection([
            ('إغلاق', 'إغلاق'),
            ('وقف نشاط', 'وقف نشاط'),
            ('وقف تداول', 'وقف تداول'),
            ('حجز تحفظي', 'حجز تحفظي'),
            ('منع من السفر', 'منع من السفر'),
            ('إيقاف سجل الحاسب الآلي', 'إيقاف سجل الحاسب الآلي'),
            ], string='تدابير مؤقتة', store=True, copy=False, readonly=False)
    general_services = fields.Selection([
            ('كهرباء', 'كهرباء'),
            ], string='الخدمات العامة', store=True, default='كهرباء', readonly=False)
    criminal = fields.Selection([
            ('استرداد العقار', 'استرداد العقار'),
            ], string='الضبطية الجنائية', store=True, default='استرداد العقار', readonly=False)
    telecom = fields.Selection([
            ('قرارات تنظيمية', 'قرارات تنظيمية'),
            ], string='اتصالات', store=True, default='قرارات تنظيمية', readonly=False)
    managerial_2 = fields.Many2one('compensation.type', string='تعويض', auto_join=True)
    managerial_3 = fields.Selection([
            ('صيانة ونظافة وتشغيل', 'صيانة ونظافة وتشغيل'),
            ('توريد', 'توريد'),
            ('نقل', 'نقل'),
            ('أشغال عامة', 'أشغال عامة'),
            ('امتياز', 'امتياز'),
            ('تأمين', 'تأمين'),
            ('بيع', 'بيع'),
            ('استثمار', 'استثمار'),
            ('قرض', 'قرض'),
            ('إشراف', 'إشراف'),
            ('إعاشة', 'إعاشة'),
            ('استشارات', 'استشارات'),
            ('إجارة', 'إجارة'),
            ('تدريب', 'تدريب'),
            ('عمل', 'عمل'),
            ('استئجار الدولة للعقار', 'استئجار الدولة للعقار'),
            ], string='عقد', store=True, copy=False, readonly=False)
    contracting = fields.Many2one('contracting.type', string='النوع', auto_join=True)
    loan = fields.Selection([
            ('قرض شخصي', 'قرض شخصي'),
            ('قرض زراعي', 'قرض زراعي'),
            ('قرض صناعي', 'قرض صناعي'),
            ('قرض سكني', 'قرض سكني'),
            ('قرض تجاري', 'قرض تجاري'),
            ('قرض تعليمي', 'قرض تعليمي'),
            ('قرض صحي', 'قرض صحي'),
            ('قرض اجتماعي', 'قرض اجتماعي'),
            ], string='قرض', store=True, copy=False, readonly=False)
    work = fields.Selection([
            ('إجازة', 'إجازة'),
            ('ندب', 'ندب'),
            ('نقل', 'نقل'),
            ('إعارة', 'إعارة'),
            ('فسخ العقد', 'فسخ العقد'),
            ('تجديد', 'تجديد'),
            ('إنهاء عقد', 'إنهاء عقد'),
            ('مستحقات عقدية', 'مستحقات عقدية'),
            ], string='عمل', store=True, copy=False, readonly=False)
    state_rental = fields.Selection([
            ('إجراء استئجار', 'إجراء استئجار'),
            ('أجرة', 'أجرة'),
            ('إخلاء', 'إخلاء'),
            ('تعويض', 'تعويض'),
            ('تمديد', 'تمديد'),
            ('تجديد', 'تجديد'),
            ('إنهاء العقد', 'إنهاء العقد'),
            ('التزامات عقدية', 'التزامات عقدية'),
            ], string='استئجار الدولة للعقار', store=True, copy=False, readonly=False)
    managerial_4 = fields.Selection([
            ('طلب تعويض من جهة الإدارة على جهة غير جهة الإدارة', 'طلب تعويض من جهة الإدارة على جهة غير جهة الإدارة'),
            ('تصفية الجمعيات التعاونية', 'تصفية الجمعيات التعاونية'),
            ('صرف عادة سنوية', 'صرف عادة سنوية'),
            ('استرداد مبالغ للجهة الإدارية دون رابطة عقدية', 'استرداد مبالغ للجهة الإدارية دون رابطة عقدية'),
            ('صرف إعانة مرضى قبل صدور قرار الهيئة الطبية العليا', 'صرف إعانة مرضى قبل صدور قرار الهيئة الطبية العليا'),
            ('صرف إعانة مرض قبل صدور قرار الهيئة الطبية العامة', 'صرف إعانة مرض قبل صدور قرار الهيئة الطبية العامة'),
            ], string='منازعة إدارية أخرى', store=True, copy=False, readonly=False)
    managerial_5 = fields.Selection([
            ('مدني - موظف عام', 'مدني - موظف عام'),
            ('مدني - موظف صحي', 'مدني - موظف صحي'),
            ('مدني - عضو هيئة تدريس جامعي', 'مدني - عضو هيئة تدريس جامعي'),
            ('مدني - معلم', 'مدني - معلم'),
            ('عسكري - ضابط', 'عسكري - ضابط'),
            ('عسكري - فرد', 'عسكري - فرد'),
            ], string='حقوق وظيفية', store=True, copy=False, readonly=False)
    civil_general = fields.Selection([
            ('بدل طبيعة عمل', 'بدل طبيعة عمل'),
            ('بدل مناطق نائية', 'بدل مناطق نائية'),
            ('بدل مهنة تدريب', 'بدل مهنة تدريب'),
            ('تذاكر سفر', 'تذاكر سفر'),
            ('تعويض عن إجازة', 'تعويض عن إجازة'),
            ('علاوة سنوية', 'علاوة سنوية'),
            ('علاوة فنية في الأرصاد', 'علاوة فنية في الأرصاد'),
            ('مكافأة حاسب آلي', 'مكافأة حاسب آلي'),
            ('مكافأة الدارسين أثناء عملهم بالخارج', 'مكافأة الدارسين أثناء عملهم بالخارج'),
            ('مكافأة الضبط الجمركي', 'مكافأة الضبط الجمركي'),
            ('مكافأة الطبيب البيطري', 'مكافأة الطبيب البيطري'),
            ('مكافأة المستشارين غير المفرغين', 'مكافأة المستشارين غير المفرغين'),
            ('مكافأة تدريب', 'مكافأة تدريب'),
            ('مكافأة خارج الدوام', 'مكافأة خارج الدوام'),
            ('مكافأة سائقي سيارات الوزراء والمرتبة الممتازة', 'مكافأة سائقي سيارات الوزراء والمرتبة الممتازة'),
            ('مكافأة مباشرة الأموال العامة', 'مكافأة مباشرة الأموال العامة'),
            ('مكافأة موزعي البريد', 'مكافأة موزعي البريد'),
            ('مكافأة نهاية الخدمة', 'مكافأة نهاية الخدمة'),
            ('بدل انتقال شهري', 'بدل انتقال شهري'),
            ('بدل ترحيل', 'بدل ترحيل'),
            ('بدل تعيين', 'بدل تعيين'),
            ('بدل تمثيل', 'بدل تمثيل'),
            ('بدل خطر', 'بدل خطر'),
            ('بدل ضرر أو عدوى', 'بدل ضرر أو عدوى'),
            ], string='موظف عام', store=True, copy=False, readonly=False)
    health_worker = fields.Selection([
            ('إجازة مرضية', 'إجازة مرضية'),
            ('إجازة وضع', 'إجازة وضع'),
            ('إجازة امتحان', 'إجازة امتحان'),
            ('إجازة دراسية', 'إجازة دراسية'),
            ('إجازة مشاركة أندية', 'إجازة مشاركة أندية'),
            ('إجازة مولود', 'إجازة مولود'),
            ('إجازة وفاة', 'إجازة وفاة'),
            ('إجازة استثنائية', 'إجازة استثنائية'),
            ('إجازة اعتيادية', 'إجازة اعتيادية'),
            ('إجازة أمومة', 'إجازة أمومة'),
            ('احتساب إجازة', 'احتساب إجازة'),
            ('إجازة مرافقة مريض', 'إجازة مرافقة مريض'),
            ('إجازة مرافقة مبتعث', 'إجازة مرافقة مبتعث'),
            ('إجازة عدة وفاة', 'إجازة عدة وفاة'),
            ('إجازة أعمال إغاثة', 'إجازة أعمال إغاثة'),
            ('بدل ابتعاث', 'بدل ابتعاث'),
            ('بدل إشراف', 'بدل إشراف'),
            ('بدل انتداب', 'بدل انتداب'),
            ('بدل انتقال شهري', 'بدل انتقال شهري'),
            ('بدل تدريب', 'بدل تدريب'),
            ('بدل ترحيل', 'بدل ترحيل'),
            ('بدل تعيين', 'بدل تعيين'),
            ('بدل تفرغ والعمل الإضافي', 'بدل تفرغ والعمل الإضافي'),
            ('بدل تكليف بأعمال إدارية', 'بدل تكليف بأعمال إدارية'),
            ('بدل تمثيل', 'بدل تمثيل'),
            ('بدل تميز', 'بدل تميز'),
            ('بدل خطر', 'بدل خطر'),
            ('بدل ضرر أو عدوى', 'بدل ضرر أو عدوى'),
            ('بدل طبيعة عمل', 'بدل طبيعة عمل'),
            ('بدل عاملين في المناطق الجبلية', 'بدل عاملين في المناطق الجبلية'),
            ('بدل قيادة سيارة إسعاف', 'بدل قيادة سيارة إسعاف'),
            ('بدل مزاولة طب شرعي', 'بدل مزاولة طب شرعي'),
            ('بدل مستشفيات الجذام وأقسام العزل', 'بدل مستشفيات الجذام وأقسام العزل'),
            ('بدل مستشفيات نفسية', 'بدل مستشفيات نفسية'),
            ('بدل مناطق نائية', 'بدل مناطق نائية'),
            ('بدل ندرة', 'بدل ندرة'),
            ('تذاكر سفر', 'تذاكر سفر'),
            ('تعويض عن إجازة', 'تعويض عن إجازة'),
            ('راتب', 'راتب'),
            ('علاوة سنوية', 'علاوة سنوية'),
            ('مكافأة تدريب', 'مكافأة تدريب'),
            ('مكافأة حاسب آلي', 'مكافأة حاسب آلي'),
            ('مكافأة خارج دوام', 'مكافأة خارج دوام'),
            ('مكافأة مباشرة الأموال العامة', 'مكافأة مباشرة الأموال العامة'),
            ('مكافأة مستخدمين عاملين في خدمة المرضى', 'مكافأة مستخدمين عاملين في خدمة المرضى'),
            ('مكافأة نهاية الخدمة', 'مكافأة نهاية الخدمة'),
            ('تحسين مستوى', 'تحسين مستوى'),
            ], string='موظف صحي', store=True, copy=False, readonly=False)
    university_worker = fields.Selection([
            ('إجازة مرضية', 'إجازة مرضية'),
            ('إجازة وضع', 'إجازة وضع'),
            ('إجازة امتحان', 'إجازة امتحان'),
            ('إجازة دراسية', 'إجازة دراسية'),
            ('إجازة مشاركة أندية', 'إجازة مشاركة أندية'),
            ('إجازة مولود', 'إجازة مولود'),
            ('إجازة وفاة', 'إجازة وفاة'),
            ('إجازة استثنائية', 'إجازة استثنائية'),
            ('إجازة اعتيادية', 'إجازة اعتيادية'),
            ('إجازة أمومة', 'إجازة أمومة'),
            ('احتساب إجازة', 'احتساب إجازة'),
            ('إجازة مرافقة مريض', 'إجازة مرافقة مريض'),
            ('إجازة مرافقة مبتعث', 'إجازة مرافقة مبتعث'),
            ('إجازة عدة وفاة', 'إجازة عدة وفاة'),
            ('إجازة أعمال إغاثة', 'إجازة أعمال إغاثة'),
            ('بدل ابتعاث', 'بدل ابتعاث'),
            ('بدل انتداب', 'بدل انتداب'),
            ('بدل انتقال شهري', 'بدل انتقال شهري'),
            ('بدل ترحيل', 'بدل ترحيل'),
            ('بدل تمثيل', 'بدل تمثيل'),
            ('بدل تعيين', 'بدل تعيين'),
            ('بدل ابتعاث', 'بدل ابتعاث'),
            ('بدل خطر', 'بدل خطر'),
            ('بدل جامعة ناشئة', 'بدل جامعة ناشئة'),
            ('بدل ضرر أو عدوى', 'بدل ضرر أو عدوى'),
            ('بدل طبيعة عمل', 'بدل طبيعة عمل'),
            ('بدل مناطق نائية', 'بدل مناطق نائية'),
            ('بدل ندرة', 'بدل ندرة'),
            ('بدل وحدات تدريسية زائدة', 'بدل وحدات تدريسية زائدة'),
            ('تذاكر سفر', 'تذاكر سفر'),
            ('تعويض عن إجازة', 'تعويض عن إجازة'),
            ('راتب', 'راتب'),
            ('علاوة سنوية', 'علاوة سنوية'),
            ('مكافأة حاسب آلي', 'مكافأة حاسب آلي'),
            ('مكافأة عمل بالإجازة الصيفية', 'مكافأة عمل بالإجازة الصيفية'),
            ('مكافأة عمل باللجان الدائمة', 'مكافأة عمل باللجان الدائمة'),
            ('مكافأة إلقاء وحدات تدريسية غير منهجية', 'مكافأة إلقاء وحدات تدريسية غير منهجية'),
            ('مكافأة مستشار غير متفرغ', 'مكافأة مستشار غير متفرغ'),
            ('مكافأة أمين المجلس العلمي', 'مكافأة أمين المجلس العلمي'),
            ('مكافأة بدل تفرغ وساعات عمل إضافي لغير الأطباء', 'مكافأة بدل تفرغ وساعات عمل إضافي لغير الأطباء'),
            ('مكافأة بدل تفرغ وساعات عمل إضافي للصيادلة وأعضاء هيئة التدريس', 'مكافأة بدل تفرغ وساعات عمل إضافي للصيادلة وأعضاء هيئة التدريس'),
            ('مكافأة تدريب', 'مكافأة تدريب'),
            ('مكافأة خارج الدوام', 'مكافأة خارج الدوام'),
            ('مكافأة رئيس قسم', 'مكافأة رئيس قسم'),
            ('مكافأة عميد كلية', 'مكافأة عميد كلية'),
            ('مكافأة نهاية الخدمة', 'مكافأة نهاية الخدمة'),
            ('مكافأة وكيل كلية', 'مكافأة وكيل كلية'),
            ('مكافأة وكيل جامعة', 'مكافأة وكيل جامعة'),
            ('مكافأة بدل تفرغ وساعات عمل إضافي للأطباء', 'مكافأة بدل تفرغ وساعات عمل إضافي للأطباء'),
            ], string='عضو هيئة تدريس جامعي', store=True, copy=False, readonly=False)
    teacher = fields.Selection([
            ('بدل انتداب', 'بدل انتداب'),
            ('بدل انتقال شهري', 'بدل انتقال شهري'),
            ('بدل تربية خاصة', 'بدل تربية خاصة'),
            ('بدل ترحيل', 'بدل ترحيل'),
            ('بدل تعيين', 'بدل تعيين'),
            ('بدل تمثيل', 'بدل تمثيل'),
            ('بدل خطر', 'بدل خطر'),
            ('بدل ضرر أو عدوى', 'بدل ضرر أو عدوى'),
            ('بدل طبيعة عمل', 'بدل طبيعة عمل'),
            ('بدل مناطق نائية', 'بدل مناطق نائية'),
            ('بدل مهنة تدريب', 'بدل مهنة تدريب'),
            ('تذاكر سفر', 'تذاكر سفر'),
            ('راتب', 'راتب'),
            ('مكافأة تدريب', 'مكافأة تدريب'),
            ('مكافأة نهاية خدمة', 'مكافأة نهاية خدمة'),
            ('بدل عاملين في المناطق الجبلية', 'بدل عاملين في المناطق الجبلية'),
            ('بدل ابتعاث', 'بدل ابتعاث'),
            ('مكافأة مدارس ليلية', 'مكافأة مدارس ليلية'),
            ('تحسين مستوى', 'تحسين مستوى'),
            ('إجازة مرضية', 'إجازة مرضية'),
            ('إجازة وضع', 'إجازة وضع'),
            ('إجازة امتحان', 'إجازة امتحان'),
            ('إجازة دراسية', 'إجازة دراسية'),
            ('إجازة مشاركة أندية', 'إجازة مشاركة أندية'),
            ('إجازة مولود', 'إجازة مولود'),
            ('إجازة وفاة', 'إجازة وفاة'),
            ('إجازة استثنائية', 'إجازة استثنائية'),
            ('إجازة اعتيادية', 'إجازة اعتيادية'),
            ('إجازة أمومة', 'إجازة أمومة'),
            ('احتساب إجازة', 'احتساب إجازة'),
            ('إجازة مرافقة مريض', 'إجازة مرافقة مريض'),
            ('إجازة مرافقة مبتعث', 'إجازة مرافقة مبتعث'),
            ('إجازة عدة وفاة', 'إجازة عدة وفاة'),
            ('إجازة أعمال إغاثة', 'إجازة أعمال إغاثة'),
            ], string='معلم', store=True, copy=False, readonly=False)
    military_officer = fields.Selection([
            ('إجازة مرضية', 'إجازة مرضية'),
            ('إجازة ميدانية', 'إجازة ميدانية'),
            ('إجازة اعتيادية', 'إجازة اعتيادية'),
            ('إجازة استثنائية', 'إجازة استثنائية'),
            ('إجازة عرضية', 'إجازة عرضية'),
            ('إجازة دراسية', 'إجازة دراسية'),
            ('إجازة مولود', 'إجازة مولود'),
            ('إجازة وفاة', 'إجازة وفاة'),
            ('إجازة مرافقة مريض', 'إجازة مرافقة مريض'),
            ('إجازة مرافقة مبتعث', 'إجازة مرافقة مبتعث'),
            ('بدل ابتعاث', 'بدل ابتعاث'),
            ('بدل إعاشة', 'بدل إعاشة'),
            ('بدل علاج في الخارج', 'بدل علاج في الخارج'),
            ('بدل انتداب', 'بدل انتداب'),
            ('بدل تعيين', 'بدل تعيين'),
            ('بدل تمثيل', 'بدل تمثيل'),
            ('بدل تنقلات', 'بدل تنقلات'),
            ('بدل ركن', 'بدل ركن'),
            ('بدل ملابس', 'بدل ملابس'),
            ('بدل منصب', 'بدل منصب'),
            ('بدل نقل', 'بدل نقل'),
            ('بدل تكليف الأعياد غير أعمال الحج', 'بدل تكليف الأعياد غير أعمال الحج'),
            ('راتب', 'راتب'),
            ('تعويض عن إجازات', 'تعويض عن إجازات'),
            ('تعويض عن توقيف', 'تعويض عن توقيف'),
            ('تعويض عن تذاكر سفر', 'تعويض عن تذاكر سفر'),
            ('علاوة قوات خاصة للمظليين', 'علاوة قوات خاصة للمظليين'),
            ('علاوة أركان', 'علاوة أركان'),
            ('علاوة إشارة', 'علاوة إشارة'),
            ('علاوة الكترونبات', 'علاوة الكترونبات'),
            ('علاوة أمن واستخبارات', 'علاوة أمن واستخبارات'),
            ('علاوة دفاع مدني', 'علاوة دفاع مدني'),
            ('علاوة فدائيين', 'علاوة فدائيين'),
            ('علاوة مران', 'علاوة مران'),
            ('علاوة مرور', 'علاوة مرور'),
            ('علاوة مساعدات فنية', 'علاوة مساعدات فنية'),
            ('علاوة مضليين', 'علاوة مضليين'),
            ('علاوة ملاحين جويين', 'علاوة ملاحين جويين'),
            ('علاوة موسيقى', 'علاوة موسيقى'),
            ('علاوة نقل', 'علاوة نقل'),
            ('علاوة بحرية', 'علاوة بحرية'),
            ('علاوة تخصص', 'علاوة تخصص'),
            ('علاوة تدريس', 'علاوة تدريس'),
            ('علاوة تمريض', 'علاوة تمريض'),
            ('علاوة توجيه نيران', 'علاوة توجيه نيران'),
            ('علاوة جوازات', 'علاوة جوازات'),
            ('علاوة خطر', 'علاوة خطر'),
            ('علاوة درع وأطقم مدرعات', 'علاوة درع وأطقم مدرعات'),
            ('علاوة سنوية', 'علاوة سنوية'),
            ('علاوة صواريخ', 'علاوة صواريخ'),
            ('علاوة صيانة', 'علاوة صيانة'),
            ('علاوة طيران', 'علاوة طيران'),
            ('علاوة دعوى ضرر', 'علاوة دعوى ضرر'),
            ('علاوة غطس', 'علاوة غطس'),
            ('علاوة فني بحث وتحري', 'علاوة فني بحث وتحري'),
            ('علاوة فني مطابع', 'علاوة فني مطابع'),
            ('علاوة فنية', 'علاوة فنية'),
            ('علاوة قفز', 'علاوة قفز'),
            ('علاوة قيادة', 'علاوة قيادة'),
            ('علاوة قيادة الدراجة النارية', 'علاوة قيادة الدراجة النارية'),
            ('علاوة مكافحة الإرهاب', 'علاوة مكافحة الإرهاب'),
            ('مكافأة اشتراك في أعمال الحج', 'مكافأة اشتراك في أعمال الحج'),
            ('مكافأة إصابة', 'مكافأة إصابة'),
            ('مكافأة تفوق', 'مكافأة تفوق'),
            ('مكافأة شهادة دراسية', 'مكافأة شهادة دراسية'),
            ('مكافأة شهادة أو إصابة من عمليات مكافحة الإرهاب', 'مكافأة شهادة أو إصابة من عمليات مكافحة الإرهاب'),
            ('مكافأة عمل بالحاسب الآلي', 'مكافأة عمل بالحاسب الآلي'),
            ('مكافأة حفظ المواد المخدرة', 'مكافأة حفظ المواد المخدرة'),
            ('مكافأة لجنة إتلاف المخدرات', 'مكافأة لجنة إتلاف المخدرات'),
            ('مكافأة مباشرة الأموال العامة', 'مكافأة مباشرة الأموال العامة'),
            ('مكافأة مراقب سلامة', 'مكافأة مراقب سلامة'),
            ('مكافأة نهاية الخدمة', 'مكافأة نهاية الخدمة'),
            ('نصف يومية الميدان', 'نصف يومية الميدان'),
            ('يومية الميدان', 'يومية الميدان'),
            ('علاوة قوات خاصة', 'علاوة قوات خاصة'),
            ('علاوة مراكز حدودية', 'علاوة مراكز حدودية'),
            ('علاوة أمن حدود', 'علاوة أمن حدود'),
            ('بدل دوريات أمنية', 'بدل دوريات أمنية'),
            ], string='ضابط', store=True, copy=False, readonly=False)
    military_person = fields.Selection([
            ('علاوة ملاحين جويين', 'علاوة ملاحين جويين'),
            ('علاوة موسيقى', 'علاوة موسيقى'),
            ('علاوة السياقة', 'علاوة السياقة'),
            ('علاوة تدريس', 'علاوة تدريس'),
            ('علاوة تمريض', 'علاوة تمريض'),
            ('علاوة توجيه نيران', 'علاوة توجيه نيران'),
            ('علاوة جوازات', 'علاوة جوازات'),
            ('علاوة خطر', 'علاوة خطر'),
            ('علاوة درع وأطقم مدرعات', 'علاوة درع وأطقم مدرعات'),
            ('علاوة سنوية', 'علاوة سنوية'),
            ('علاوة صواريخ', 'علاوة صواريخ'),
            ('علاوة صيانة', 'علاوة صيانة'),
            ('علاوة عدوى وضرر', 'علاوة عدوى وضرر'),
            ('علاوة غطس', 'علاوة غطس'),
            ('علاوة فني مطابع', 'علاوة فني مطابع'),
            ('علاوة فنية', 'علاوة فنية'),
            ('علاوة فني بحث وتحري', 'علاوة فني بحث وتحري'),
            ('علاوة قيادة دراجة نارية', 'علاوة قيادة دراجة نارية'),
            ('علاوة مكافحة الإرهاب', 'علاوة مكافحة الإرهاب'),
            ('علاوة مناطق نائية', 'علاوة مناطق نائية'),
            ('مكافأة اشتراك في أعمال الحج', 'مكافأة اشتراك في أعمال الحج'),
            ('مكافأة إصابة', 'مكافأة إصابة'),
            ('مكافأة أعمال جليلة', 'مكافأة أعمال جليلة'),
            ('مكافأة تفوق', 'مكافأة تفوق'),
            ('مكافأة شهادة دراسية', 'مكافأة شهادة دراسية'),
            ('مكافأة شهادة أو إصابة من عمليات مكافحة الإرهاب', 'مكافأة شهادة أو إصابة من عمليات مكافحة الإرهاب'),
            ('مكافأة عمل بالحاسب الآلي', 'مكافأة عمل بالحاسب الآلي'),
            ('مكافأة حفظ المواد المخدرة', 'مكافأة حفظ المواد المخدرة'),
            ('مكافأة لجنة إتلاف المخدرات', 'مكافأة لجنة إتلاف المخدرات'),
            ('مكافأة مباشرة الأموال العامة', 'مكافأة مباشرة الأموال العامة'),
            ('مكافأة مراقب سلامة', 'مكافأة مراقب سلامة'),
            ('مكافأة نهاية خدمة', 'مكافأة نهاية خدمة'),
            ('نصف يومية الميدان', 'نصف يومية الميدان'),
            ('يومية الميدان', 'يومية الميدان'),
            ('بدل ابتعاث', 'بدل ابتعاث'),
            ('بدل إعاشة', 'بدل إعاشة'),
            ('بدل علاج في الخارج', 'بدل علاج في الخارج'),
            ('بدل انتداب', 'بدل انتداب'),
            ('بدل ترحيل', 'بدل ترحيل'),
            ('بدل تعيين', 'بدل تعيين'),
            ('بدل تمثيل', 'بدل تمثيل'),
            ('بدل تنقلات', 'بدل تنقلات'),
            ('بدل ملابس', 'بدل ملابس'),
            ('بدل نقل', 'بدل نقل'),
            ('بدل تكليف الأعياد غير أعمال الحج', 'بدل تكليف الأعياد غير أعمال الحج'),
            ('راتب', 'راتب'),
            ('تعويض عن إجازات', 'تعويض عن إجازات'),
            ('تعويض عن التوقيف', 'تعويض عن التوقيف'),
            ('تعويض عن تذاكر السفر', 'تعويض عن تذاكر السفر'),
            ('علاوة قوات خاصة للمظليين', 'علاوة قوات خاصة للمظليين'),
            ('علاوة إشارة', 'علاوة إشارة'),
            ('علاوة الكترونيات', 'علاوة الكترونيات'),
            ('علاوة أمن واستخبارات', 'علاوة أمن واستخبارات'),
            ('علاوة دفاع مدني', 'علاوة دفاع مدني'),
            ('علاوة فدائيين', 'علاوة فدائيين'),
            ('علاوة مران', 'علاوة مران'),
            ('علاوة مرور', 'علاوة مرور'),
            ('علاوة مساعدات فنية', 'علاوة مساعدات فنية'),
            ('علاوة مظليين', 'علاوة مظليين'),
            ('علاوة حدود نائية', 'علاوة حدود نائية'),
            ('علاوة إدارة مكتبية', 'علاوة إدارة مكتبية'),
            ('علاوة دوريات أمن', 'علاوة دوريات أمن'),
            ('بدل ساعي بريد', 'بدل ساعي بريد'),
            ('إجازة استثنائية', 'إجازة استثنائية'),
            ('إجازة اعتيادية', 'إجازة اعتيادية'),
            ('إجازة دراسية', 'إجازة دراسية'),
            ('إجازة عرضية', 'إجازة عرضية'),
            ('إجازة مرافقة مبتعث', 'إجازة مرافقة مبتعث'),
            ('إجازة مرافقة مريض', 'إجازة مرافقة مريض'),
            ('إجازة مرضية', 'إجازة مرضية'),
            ('إجازة مولود', 'إجازة مولود'),
            ('إجازة ميدانية', 'إجازة ميدانية'),
            ('إجازة وفاة', 'إجازة وفاة'),
            ], string='فرد', store=True, copy=False, readonly=False)
    managerial_6 = fields.Many2one('discipline.type', string='تأديب', auto_join=True)
    managerial_7 = fields.Many2one('retirement.type', string='تقاعد', auto_join=True)
    managerial_8 = fields.Many2one('judicial.type', string='طلبات قضائية', auto_join=True)
    managerial_9 = fields.Selection([
            ('استثمار', 'استثمار'),
            ('المحافظة على الذوق العام', 'المحافظة على الذوق العام'),
            ('أمن وسلامة', 'أمن وسلامة'),
            ('إنتاج المواد التعليمية', 'إنتاج المواد التعليمية'),
            ('أندية السيارات والدراجات النارية', 'أندية السيارات والدراجات النارية'),
            ('بلدية', 'بلدية'),
            ('تجارة وصناعة', 'تجارة وصناعة'),
            ('تسجيل عيني للعقار', 'تسجيل عيني للعقار'),
            ('ثقافة وإعلام', 'ثقافة وإعلام'),
            ('حج', 'حج'),
            ('حماية البيئة', 'حماية البيئة'),
            ('خدمات عامة', 'خدمات عامة'),
            ('زراعة ومياه', 'زراعة ومياه'),
            ('سياحة وآثار', 'سياحة وآثار'),
            ('صحية', 'صحية'),
            ('مالية', 'مالية'),
            ('مهن حرة', 'مهن حرة'),
            ('نقل', 'نقل'),
            ('الاتصالات وتقنية المعلومات', 'الاتصالات وتقنية المعلومات'),
            ], string='غرامات', store=True, copy=False, readonly=False)
    fine_1 = fields.Selection([
            ('استثمار أجنبي', 'استثمار أجنبي'),
            ('استثمار تعديني', 'استثمار تعديني'),
            ], string='استثمار', store=True, copy=False, readonly=False)
    fine_2 = fields.Selection([
            ('التصرفات الخادشة للحياء', 'التصرفات الخادشة للحياء'),
            ('إخافة مرتادي الأماكن العامة', 'إخافة مرتادي الأماكن العامة'),
            ('ارتداء ملابس تحوي عبارات أو صور عنصرية', 'ارتداء ملابس تحوي عبارات أو صور عنصرية'),
            ('ارتداء ملابس تحوي عبارات أو صور مخلة', 'ارتداء ملابس تحوي عبارات أو صور مخلة'),
            ('ارتداء ملابس غير لائقة', 'ارتداء ملابس غير لائقة'),
            ('استعمال مقاعد ومرافق كبار السن وذوي الاحتياجات الخاصة', 'استعمال مقاعد ومرافق كبار السن وذوي الاحتياجات الخاصة'),
            ('إشعال النار في غير الأماكن المسموح بها', 'إشعال النار في غير الأماكن المسموح بها'),
            ('البصق في غير الأماكن المخصصة', 'البصق في غير الأماكن المخصصة'),
            ('الرسم على الأماكن العامة دون ترخيص', 'الرسم على الأماكن العامة دون ترخيص'),
            ('الرسم على وسائل النقل دون ترخيص', 'الرسم على وسائل النقل دون ترخيص'),
            ('إلقاء النفايات في غير الأماكن المخصصة', 'إلقاء النفايات في غير الأماكن المخصصة'),
            ('الكتابة على الأماكن العامة دون ترخيص', 'الكتابة على الأماكن العامة دون ترخيص'),
            ('الكتابة على وسائل النقل دون ترخيص', 'الكتابة على وسائل النقل دون ترخيص'),
            ('إيذاء مرتادي الأماكن العامة', 'إيذاء مرتادي الأماكن العامة'),
            ('تجاوز الدخول إلى الأماكن العامة', 'تجاوز الدخول إلى الأماكن العامة'),
            ('تخطي طوابير الانتظار', 'تخطي طوابير الانتظار'),
            ('تشغيل الموسيقى في أوقات الأذان وإقامة الصلاة', 'تشغيل الموسيقى في أوقات الأذان وإقامة الصلاة'),
            ('تصوير أشخاص دون إذن', 'تصوير أشخاص دون إذن'),
            ('تصوير حوادث دون إذن من أطرافها', 'تصوير حوادث دون إذن من أطرافها'),
            ('تعريض مرتادي الأماكن العامة للخطر', 'تعريض مرتادي الأماكن العامة للخطر'),
            ('توزيع منشورات في الأماكن العامة دون ترخيص', 'توزيع منشورات في الأماكن العامة دون ترخيص'),
            ('رفع صوت الموسيقى داخل الأحياء السكنية', 'رفع صوت الموسيقى داخل الأحياء السكنية'),
            ('عدم إزالة مخلفات الحيوانات الأليفة', 'عدم إزالة مخلفات الحيوانات الأليفة'),
            ('وضع عبارات أو صور عنصرية على وسائل النقل', 'وضع عبارات أو صور عنصرية على وسائل النقل'),
            ('وضع ملصقات في الأماكن العامة دون ترخيص', 'وضع ملصقات في الأماكن العامة دون ترخيص'),
            ('وضع عبارات أو صور مخلة على وسائل النقل', 'وضع عبارات أو صور مخلة على وسائل النقل'),
            ], string='المحافظة على الذوق العام', store=True, copy=False, readonly=False)
    fine_3 = fields.Selection([
            ('حراسة أمنية خاصة', 'حراسة أمنية خاصة'),
            ('غرامات جوازات', 'غرامات جوازات'),
            ('غرامات دفاع مدني', 'غرامات دفاع مدني'),
            ('غرامات مرورية', 'غرامات مرورية'),
            ('نظام شموس الأمني', 'نظام شموس الأمني'),
            ], string='أمن وسلامة', store=True, copy=False, readonly=False)
    fine_6 = fields.Many2one('fine.type', string='بلدية', auto_join=True)
    fine_7 = fields.Selection([
            ('أسماء تجارية', 'أسماء تجارية'),
            ('حماية مستهلك', 'حماية مستهلك'),
            ('حماية منافسة', 'حماية منافسة'),
            ('سجل تجاري', 'سجل تجاري'),
            ('مصانع', 'مصانع'),
            ('معادن ثقيلة وأحجار كريمة', 'معادن ثقيلة وأحجار كريمة'),
            ('نقل النقود والمعادن الثمينة والمستندات ذات القيمة', 'نقل النقود والمعادن الثمينة والمستندات ذات القيمة'),
            ('وكالات تجارية', 'وكالات تجارية'),
            ], string='تجارة وصناعة', store=True, copy=False, readonly=False)
    fine_9 = fields.Selection([
            ('إعلام مرئي ومسموع', 'إعلام مرئي ومسموع'),
            ('نظام الإيداع', 'نظام الإيداع'),
            ], string='ثقافة وإعلام', store=True, copy=False, readonly=False)
    fine_10 = fields.Selection([
            ('خدمة حجاج', 'خدمة حجاج'),
            ('نقل حجاج', 'نقل حجاج'),
            ], string='حج', store=True, copy=False, readonly=False)
    fine_11 = fields.Selection([
            ('اتجار بالكائنات الفطرية', 'اتجار بالكائنات الفطرية'),
            ('مناطق محمية', 'مناطق محمية'),
            ], string='حماية البيئة', store=True, copy=False, readonly=False)
    fine_12 = fields.Selection([
            ('بريد', 'بريد'),
            ('كهرباء', 'كهرباء'),
            ('مرافق عامة', 'مرافق عامة'),
            ('مياه', 'مياه'),
            ], string='خدمات عامة', store=True, copy=False, readonly=False)
    fine_13 = fields.Selection([
            ('أسمدة ومحسنات تربة', 'أسمدة ومحسنات تربة'),
            ('أعلاف', 'أعلاف'),
            ('تربية نحل', 'تربية نحل'),
            ('ثروات مائية حية', 'ثروات مائية حية'),
            ('ثروة حيوانية', 'ثروة حيوانية'),
            ('حجر زراعي', 'حجر زراعي'),
            ('رفق بالحيوان', 'رفق بالحيوان'),
            ('زراعة عضوية', 'زراعة عضوية'),
            ('صيد حيوانات', 'صيد حيوانات'),
            ('مبيدات', 'مبيدات'),
            ('مراعي وغابات', 'مراعي وغابات'),
            ('مصادر مياه', 'مصادر مياه'),
            ], string='زراعة ومياه', store=True, copy=False, readonly=False)
    fine_14 = fields.Selection([
            ('آثار و متاحف', 'آثار و متاحف'),
            ('حماية التراث المخطوط', 'حماية التراث المخطوط'),
            ('سياحة', 'سياحة'),
            ], string='سياحة وآثار', store=True, copy=False, readonly=False)
    fine_15 = fields.Selection([
            ('إدارة النفايات الصحية', 'إدارة النفايات الصحية'),
            ('تداول بدائل حليب الأم', 'تداول بدائل حليب الأم'),
            ('رعاية صحية نفسية', 'رعاية صحية نفسية'),
            ('ضمان الصحي تعاوني', 'ضمان الصحي تعاوني'),
            ('مؤسسات صحية خاصة', 'مؤسسات صحية خاصة'),
            ('مختبرات خاصة', 'مختبرات خاصة'),
            ('مزاولة مهن صحية', 'مزاولة مهن صحية'),
            ('مكافحة تدخين', 'مكافحة تدخين'),
            ('منتجات تجميل', 'منتجات تجميل'),
            ('منشآت ومستحضرات صيدلانية', 'منشآت ومستحضرات صيدلانية'),
            ], string='صحية', store=True, copy=False, readonly=False)
    fine_16 = fields.Selection([
            ('ضريبة دخل', 'ضريبة دخل'),
            ('معلومات ائتمانية', 'معلومات ائتمانية'),
            ], string='مالية', store=True, copy=False, readonly=False)
    fine_17 = fields.Selection([
            ('تعقيب', 'تعقيب'),
            ('محاسبين قانونيين', 'محاسبين قانونيين'),
            ('محاماة', 'محاماة'),
            ('مقيمين معتمدين', 'مقيمين معتمدين'),
            ('مهندسين', 'مهندسين'),
            ], string='مهن حرة', store=True, copy=False, readonly=False)
    fine_18 = fields.Selection([
            ('الخطوط الحديدية', 'الخطوط الحديدية'),
            ('الطرق البرية', 'الطرق البرية'),
            ('الطيران المدني', 'الطيران المدني'),
            ('الموانئ والمرافئ', 'الموانئ والمرافئ'),
            ], string='نقل', store=True, copy=False, readonly=False)
    fine_19 = fields.Selection([
            ('اتصالات', 'اتصالات'),
            ('تعاملات إلكترونية', 'تعاملات إلكترونية'),
            ], string='الاتصالات وتقنية المعلومات', store=True, copy=False, readonly=False)    
    court = fields.Selection([
            ('المحكمة العامة', 'المحكمة العامة'),
            ('المحكمة التجارية', 'المحكمة التجارية'),
            ('المحكمة الإدارية', 'المحكمة الإدارية'),
            ('محكمة الأحوال الشخصية', 'محكمة الأحوال الشخصية'),
            ('المحكمة العمالية', 'المحكمة العمالية'),
            ('محكمة التنفيذ', 'محكمة التنفيذ'),
            ('تحكيم', 'تحكيم'),
            ('اخرى', 'اخرى')
            ], string='المحكمة', store=True, copy=False, readonly=False, tracking=True)
    litigation_state = fields.Selection([
        ('تقييد الدعوى', 'تقييد الدعوى'),
        ('لم يتم قيدها', 'لم يتم قيدها'),
        ('الصلح', 'الصلح'),
        ('تسوية ودياً', 'تسوية ودياً'),
        ('قيد النظر لدى المحكمة الابتدائية', 'قيد النظر لدى المحكمة الابتدائية'),
        ('المحكمة الابتدائية', 'المحكمة الابتدائية'),
        ('حكم ابتدائي', 'حكم ابتدائي'),
        ('حكم مبدئي', 'حكم مبدئي'),
        ('حكم ابتدائي لصالح العميل', 'حكم ابتدائي لصالح العميل'),
        ('حكم ابتدائي معترض عليه', 'حكم ابتدائي معترض عليه'),
        ('قيد النظر', 'قيد النظر'),
        ('قيد النظر لدى محكمة الاستئناف', 'قيد النظر لدى محكمة الاستئناف'),
        ('محكمة الاستئناف', 'محكمة الاستئناف'),
        ('عادت للمحكمة الابتدائية بملاحظات', 'عادت للمحكمة الابتدائية بملاحظات'),
        ('حكم نهائي', 'حكم نهائي'),
        ('التنفيذ', 'التنفيذ'),
        ('مشطوبة', 'مشطوبة'),
        ('موقفة', 'موقفة'),
        ('التماس إعادة نظر', 'التماس إعادة نظر'),
        ('معترض عليها', 'معترض عليها'),
        ('انتهت بحكم قضائي', 'انتهت بحكم قضائي'),
        ('انتهت صلحاً', 'اانتهت صلحاً'),
        ('انتهت', 'انتهت')
        ], string='حالة القضية', store=True, copy=False, readonly=False, default='تقييد الدعوى', tracking=True)
    client_representative_state = fields.Selection([
            ('رئيس مجلس الإدارة', 'رئيس مجلس الإدارة'),
            ('مدير الشركة', 'مدير الشركة'),
            ('صاحب المؤسسة', 'صاحب المؤسسة'),
            ('ناظر الوقف', 'ناظر الوقف'),
            ('ممثل جهة حكومية', 'ممثل جهة حكومية'),
            ('أصالة عن نفسه', 'أصالة عن نفسه')
            ], string='صفة ممثل الموكل', store=True, copy=False, readonly=False, tracking=True)
    opponent_representative_state = fields.Selection([
            ('رئيس مجلس الإدارة', 'رئيس مجلس الإدارة'),
            ('مدير الشركة', 'مدير الشركة'),
            ('صاحب المؤسسة', 'صاحب المؤسسة'),
            ('ناظر الوقف', 'ناظر الوقف'),
            ('ممثل جهة حكومية', 'ممثل جهة حكومية'),
            ('أصالة عن نفسه', 'أصالة عن نفسه'),
            ('محددة', 'محددة')
            ], string='صفة ممثل الخصم', store=True, copy=False, readonly=False, tracking=True)
    client_state = fields.Selection([
            ('مدعي', 'مدعي'),
            ('مدعي عليه', 'مدعي عليه'),
            ('محتكم', 'محتكم'),
            ('محتكم عليه', 'محتكم عليه'),
            ('مدخل', 'مدخل'),
            ('مستأنف', 'مستأنف'),
            ('مستأنف ضده', 'مستأنف ضده')
            ], string='صفة الموكل', store=True, copy=False, readonly=False, tracking=True)
    city = fields.Selection([
            ('الرياض', 'الرياض'),
            ('المدينة المنورة', 'المدينة المنورة'),
            ('جدة', 'جدة'),
            ('الخبر', 'الخبر'),
            ('مكة المكرمة','مكة المكرمة'),
            ('الاحساء','الاحساء'),
            ('الطائف','الطائف'),('ابها','ابها'),
            ('خميس مشيط','خميس مشيط'),
            ('عفيف','عفيف'),
            ('عرعر','عرعر'),
            ('أبقيق','أبقيق'),
            ('بريدة','بريدة'),
            ('بيشة','بيشة'),
            ('الباحة','الباحة'),
            ('الظهران','الظهران'),
            ('الدمام','الدمام'),
            ('ضرما','ضرما'),
            ('تبوك','تبوك'),
            ('القطيف','القطيف'),
            ('خميس مشيط','خميس مشيط'),
            ('حفر الباطن','حفر الباطن'),
            ('الجبيل','الجبيل'),
            ('الخرج','الخرج'),
            ('حائل','حائل'),
            ('نجران','نجران'),
            ('ينبع','ينبع'),
            ('صبيا','صبيا'),
            ('الدوادمي','الدوادمي'),
            ('أبو عريش','أبو عريش'),
            ('القنفذة','القنفذة'),
            ('محايل','محايل'),
            ('سكاكا','سكاكا'),
            ('عرعر','عرعر'),
            ('عنيزة','عنيزة'),
            ('القريات','القريات'),
            ('صامطة','صامطة'),
            ('جازان','جازان'),
            ('المجمعة','المجمعة'),
            ('القويعية','القويعية'),
            ('الرس','الرس'),
            ('وادي الدواسر','وادي الدواسر'),
            ('بحرة','بحرة'),
            ('الباحة','الباحة'),
            ('الجموم','الجموم'),
            ('رابغ','رابغ'),
            ('شرورة','شرورة'),
            ('الليث','الليث'),
            ('رفحاء','رفحاء'),
            ('عفيف','عفيف'),
            ('العرضيات','العرضيات'),
            ('العارضة','العارضة'),
            ('الخفجي','الخفجي'),
            ('بالقرن','بالقرن'),
            ('الدرعية','الدرعية'),
            ('ضمد','ضمد'),
            ('طبرجل','طبرجل'),
            ('بيش','بيش'),
            ('الزلفي','الزلفي'),
            ('الدرب','الدرب'),
            ('الافلاج','الافلاج'),
            ('سراة عبيدة','سراة عبيدة'),
            ('رجال المع','رجال المع'),
            ('بلجرشي','بلجرشي'),
            ('الحائط','الحائط'),
            ('ميسان','ميسان'),
            ('بدر','بدر'),
            ('املج','املج'),
            ('رأس تنوره','رأس تنوره'),
            ('المهد','المهد'),
            ('الدائر','الدائر'),
            ('البكيريه','البكيريه'),
            ('البدائع','البدائع'),
            ('خليص','خليص'),
            ('الحناكية','الحناكية'),
            ('العلا','العلا'),
            ('الطوال','الطوال'),
            ('النماص','النماص'),
            ('المجاردة','المجاردة'),
            ('بقيق','بقيق'),
            ('تثليث','تثليث'),
            ('المخواة','المخواة'),
            ('النعيرية','النعيرية'),
            ('الوجه','الوجه'),
            ('ضباء','ضباء'),
            ('بارق','بارق'),
            ('طريف','طريف'),
            ('خيبر','خيبر'),
            ('أضم','أضم'),
            ('النبهانية','النبهانية'),
            ('رنيه','رنيه'),
            ('دومة الجندل','دومة الجندل'),
            ('المذنب','المذنب'),
            ('تربه','تربه'),
            ('ظهران الجنوب','ظهران الجنوب'),
            ('حوطة بني تميم','حوطة بني تميم'),
            ('الخرمة','الخرمة'),
            ('قلوه','قلوه'),
            ('شقراء','شقراء'),
            ('المويه','المويه'),
            ('المزاحمية','المزاحمية'),
            ('الأسياح','الأسياح'),
            ('بقعاء','بقعاء'),
            ('السليل','السليل'),
            ('تيماء','تيماء')
            ], string='المدينة', store=True, copy=False, readonly=False, tracking=True)    
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('confirm', 'بإنتظار موافقة المدير'),
        ('suspended', 'معلقة'),
        ('Approve', 'لدى العميل'),
        ('Refuse', 'مرفوضة'),
        ('close', 'مغلقة')
        ], string='الإجراءات الداخلية', store=True, copy=False, readonly=False, default='draft')
    service_standard = fields.Selection([
        ('غير معقد', 'غير معقد'),
        ('متوسطة التعقيد', 'متوسطة التعقيد'),
        ('عالي التعقيد', 'عالي التعقيد'),
        ], string='معيار الخدمة', store=True, copy=False)
    customer_rating = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], default='0', index=True, string="تقييم العميل", tracking=True)
    customer_response=fields.Text("ملاحظات العميل", tracking=True)

    
    
    lawsuit = fields.Char(compute='get_lawsuit', string='الدعوى')
    
    def get_lawsuit(self):
        for litigation in self:
            lawsuit = False
            if litigation.case_type:
                if litigation.case_type == 'أحوال شخصية':
                    lawsuit = 'أحوال شخصية'
                    if litigation.personal_status_type:
                        lawsuit = 'أحوال شخصية: ' + litigation.personal_status_type.name
                elif litigation.case_type == 'تنفيذ':
                    lawsuit = 'تنفيذ'
                    if litigation.execute_type:
                        lawsuit = 'تنفيذ: ' + litigation.execute_type.name
                elif litigation.case_type == 'جزائية':
                    lawsuit = 'جزائية'
                    if litigation.penal_type:
                        lawsuit = 'جزائية: ' + litigation.penal_type.name
                elif litigation.case_type == 'عامة':
                    lawsuit = 'عامة'
                    if litigation.general_type:
                        lawsuit = 'عامة: ' + litigation.general_type.name
                elif litigation.case_type == 'عمالية':
                    lawsuit = 'عمالية'
                    if litigation.labor_type:
                        lawsuit = 'عمالية: ' + litigation.labor_type.name
                elif litigation.case_type == 'إدارية':
                    lawsuit = 'إدارية'
                    if litigation.managerial == 'قرار':
                        if litigation.managerial_1 == 'نزع ملكية':
                            lawsuit = 'إدارية: ' + litigation.expropriation.name
                        elif litigation.managerial_1 == 'تراخيص':
                            lawsuit = ('إدارية: ' + litigation.licenses_1 + ' تراخيص ' + litigation.licenses) 
                        elif litigation.managerial_1 == 'ملكية فكرية':
                            lawsuit = 'إدارية: ' + litigation.invention.name
                        elif litigation.managerial_1 == 'تجارة وصناعة':
                            lawsuit = 'إدارية: ' + litigation.trade
                        elif litigation.managerial_1 == 'صحية':
                            lawsuit = 'إدارية: ' + litigation.health.name
                        elif litigation.managerial_1 == 'انتخابات':
                            lawsuit = 'إدارية: ' + litigation.election
                        elif litigation.managerial_1 == 'أجانب':
                            lawsuit = 'إدارية: ' + litigation.foregners
                        elif litigation.managerial_1 == 'عقار':
                            lawsuit = 'إدارية: ' + litigation.estate
                        elif litigation.managerial_1 == 'مالية':
                            lawsuit = 'إدارية: ' + litigation.finance
                        elif litigation.managerial_1 == 'خدمة مدنية':
                            lawsuit = ('إدارية: ' + litigation.civil_service + ' خدمة مدنية ')
                        elif litigation.managerial_1 == 'خدمة عسكرية':
                            lawsuit = ('إدارية: ' + litigation.military_service + ' خدمة عسكرية ')
                        elif litigation.managerial_1 == 'تعليمية':
                            lawsuit = 'إدارية: ' + litigation.educational
                        elif litigation.managerial_1 == 'وظائف خاصة':
                            lawsuit = 'إدارية: ' + litigation.special_jobs
                        elif litigation.managerial_1 == 'جمعيات النفع العام':
                            lawsuit = 'إدارية: ' + 'جمعيات النفع العام'
                        elif litigation.managerial_1 == 'أحوال مدنية':
                            lawsuit = 'إدارية: ' + litigation.civil_status
                        elif litigation.managerial_1 == 'تخطيط عمراني':
                            lawsuit = 'إدارية: ' + litigation.urban
                        elif litigation.managerial_1 == 'تدابير مؤقتة':
                            lawsuit = 'إدارية: ' + litigation.temp_measure
                        elif litigation.managerial_1 == 'خدمات عامة':
                            lawsuit = 'إدارية: ' + litigation.general_services
                        elif litigation.managerial_1 == 'الضبطية الجنائية':
                            lawsuit = 'إدارية: ' + litigation.criminal
                        elif litigation.managerial_1 == 'اتصالات':
                            lawsuit = 'إدارية: ' + litigation.telecom
                    elif litigation.managerial == 'تعويض':
                        lawsuit = 'إدارية: ' + litigation.managerial_2.name
                    elif litigation.managerial == 'عقد':
                        if litigation.managerial_3 == 'قرض':
                            lawsuit = 'إدارية: ' + litigation.loan
                        elif litigation.managerial_3 == 'عمل':
                            lawsuit = 'إدارية: ' + litigation.work
                        elif litigation.managerial_3 == 'استئجار الدولة للعقار':
                            lawsuit = 'إدارية: ' + litigation.state_rental
                        else:
                            lawsuit = 'إدارية: ' + litigation.contracting.name
                    elif litigation.managerial == 'منازعة إدارية أخرى':
                        lawsuit = 'إدارية: ' + litigation.managerial_4
                    elif litigation.managerial == 'حقوق وظيفية':
                        if litigation.managerial_5 == 'مدني - موظف عام':
                            lawsuit = ('إدارية: ' + litigation.civil_general + ' لموظف عام ')
                        elif litigation.managerial_5 == 'مدني - موظف صحي':
                            lawsuit = ('إدارية: ' + litigation.health_worker + ' لموظف صحي ')
                        elif litigation.managerial_5 == 'مدني - عضو هيئة تدريس جامعي':
                            lawsuit = ('إدارية: ' + litigation.university_worker + ' لعضو هيئة تدريس جامعي ')
                        elif litigation.managerial_5 == 'مدني - معلم':
                            lawsuit = ('إدارية: ' + litigation.teacher + ' لمعلم ')
                        elif litigation.managerial_5 == 'عسكري - ضابط':
                            lawsuit = ('إدارية: ' + litigation.military_officer + ' لضابط ')
                        elif litigation.managerial_5 == 'عسكري - فرد':
                            lawsuit = ('إدارية: ' + litigation.military_person + ' لفرد ')
                    elif litigation.managerial == 'تأديب':
                        lawsuit = 'إدارية: ' + litigation.managerial_6.name
                    elif litigation.managerial == 'تقاعد':
                        lawsuit = 'إدارية: ' + litigation.managerial_7.name
                    elif litigation.managerial == 'طلبات قضائية':
                        lawsuit = 'إدارية: ' + litigation.managerial_8.name
                    elif litigation.managerial == 'غرامات':
                        if litigation.managerial_9 == 'استثمار':
                            lawsuit = ('إدارية: ' + 'غرامة' + litigation.fine_1)
                        elif litigation.managerial_9 == 'المحافظة على الذوق العام':
                            lawsuit = ('إدارية: ' + 'غرامة' + litigation.fine_2)
                        elif litigation.managerial_9 == 'أمن وسلامة':
                            lawsuit = ('إدارية: ' + 'غرامة' + litigation.fine_3)
                        elif litigation.managerial_9 == 'إنتاج المواد التعليمية':
                            lawsuit = ('إدارية: ' + 'غرامة' + 'إنتاج المواد التعليمية')
                        elif litigation.managerial_9 == 'أندية السيارات والدراجات النارية':
                            lawsuit = ('إدارية: ' + 'غرامة' + 'أندية السيارات والدراجات النارية')
                        elif litigation.managerial_9 == 'بلدية':
                            lawsuit = ('إدارية: ' + 'غرامة' + litigation.fine_6.name)
                        elif litigation.managerial_9 == 'تجارة وصناعة':
                            lawsuit = ('إدارية: ' + 'غرامة' + litigation.fine_7)
                        elif litigation.managerial_9 == 'تسجيل عيني للعقار':
                            lawsuit = ('إدارية: ' + 'غرامة' + 'تسجيل عيني للعقار')
                        elif litigation.managerial_9 == 'ثقافة وإعلام':
                            lawsuit = ('إدارية: ' + 'غرامة' + litigation.fine_9)
                        elif litigation.managerial_9 == 'حج':
                            lawsuit = ('إدارية: ' + 'غرامة' + litigation.fine_10)
                        elif litigation.managerial_9 == 'حماية البيئة':
                            lawsuit = ('إدارية: ' + 'غرامة' + litigation.fine_11)
                        elif litigation.managerial_9 == 'خدمات عامة':
                            lawsuit = ( 'غرامة' + litigation.fine_12)
                        elif litigation.managerial_9 == 'زراعة ومياه':
                            lawsuit = ('إدارية: ' + 'غرامة' + litigation.fine_13)
                        elif litigation.managerial_9 == 'سياحة وآثار':
                            lawsuit = ('إدارية: ' + 'غرامة' + litigation.fine_14)
                        elif litigation.managerial_9 == 'صحية':
                            lawsuit = ('إدارية: ' + 'غرامة' + litigation.fine_15)
                        elif litigation.managerial_9 == 'مالية':
                            lawsuit = ('إدارية: ' + 'غرامة' + litigation.fine_16)
                        elif litigation.managerial_9 == 'مهن حرة':
                            lawsuit = ('إدارية: ' + 'غرامة' + litigation.fine_17)
                        elif litigation.managerial_9 == 'نقل':
                            lawsuit = ('إدارية: ' + 'غرامة' + litigation.fine_18)
                        elif litigation.managerial_9 == 'الاتصالات وتقنية المعلومات':
                            lawsuit = ('إدارية: ' + 'غرامة' + litigation.fine_19)
                    elif litigation.managerial == 'طلبات أوامر الحجز':
                        lawsuit = 'إدارية: ' + 'طلبات أوامر الحجز'
                    elif litigation.managerial == 'طلبات تنفيذ مقدمة من جهة إدارية':
                        lawsuit = 'إدارية: ' + 'طلبات تنفيذ مقدمة من جهة إدارية'
                elif litigation.case_type == 'تجارية':
                    lawsuit = 'تجارية'
                    if litigation.commercial_type:
                        lawsuit = 'تجارية: ' + litigation.commercial_type.name
                elif litigation.case_type == 'اخرى':
                    if litigation.other:
                        lawsuit = litigation.other
            if lawsuit:
                litigation.lawsuit = lawsuit
            else:
                litigation.lawsuit = False
                
    @api.depends('city','caliming_date','litigation_number','opponent','circuit','case_amount','opponent_representative','summary',
                 'case_type','establishment_date','client_state','opponent_representative_state','client_representative_state'
                 ,'litigation_state','court','opponent_representative','client_representative','success_possibility'
                 ,'partner_id','personal_status','execute','penal','general','other','appeal_number','appeal_circuit'
                 ,'appeal_date','opponent_according','client_according')
    def _entry_progress(self):
        for litigation in self:
            o1 = 0          
            o2 = 0          
            o3 = 0         
            o4 = 0  
            o5 = 0
            o6 = 0        
            o7 = 0          
            o8 = 0           
            o9 = 0          
            o10 = 0          
            o11 = 0           
            o12 = 0           
            o13 = 0          
            o14 = 0
            o15 = 0
            o16 = 0  
            o17 = 0        
            o18 = 0    
            o19 = 0   
            o20 = 0   
            o21 = 0   
            o22 = 0   
            o23 = 0   
            o24 = 0   
            o25 = 0   
            no = 0
            if litigation.city:
                o1 = 1
            if litigation.caliming_date:
                o2 = 1
            if litigation.litigation_number:
                o3 = 1
            if litigation.opponent:
                o4 = 1
            if litigation.circuit:
                o5 = 1
            if litigation.case_amount:
                o6 = 1
            if litigation.opponent_representative:
                o7 = 1
            if litigation.summary:
                o8 = 1
            if litigation.case_type:
                o9 = 1
                if litigation.personal_status: 
                    o20 = 1
                elif litigation.execute:
                    o20 = 1
                elif litigation.penal:
                    o20 = 1
                elif litigation.general:
                    o20 = 1
                elif litigation.other:
                    o20 = 1            
            if litigation.establishment_date:
                o10 = 1
            if litigation.client_state:
                o11 = 1
            if litigation.opponent_representative_state:
                o12 = 1
            if litigation.client_representative_state:
                o13 = 1
            if litigation.litigation_state:
                o14 = 1
            if litigation.court:
                o15 = 1
            if litigation.opponent_representative:
                o16 = 1
            if litigation.client_representative:
                o17 = 1
            if litigation.success_possibility:
                o18 = 1
            if litigation.partner_id:
                o19 = 1
            if litigation.opponent_according:
                o24 = 1
            if litigation.client_according:
                o25 = 1
            if litigation.litigation_state == 'قيد النظر لدى محكمة الاستئناف':
                no = 25
                if litigation.appeal_number: 
                    o21 = 1
                if litigation.appeal_circuit:
                    o22 = 1
                if litigation.appeal_date:
                    o23 = 1
            else:
                no = 22
        litigation.entry_progress = ((o1 + o2 + o3 + o4 + o5 + o6 + o7 + o8 + o9 + o10 + o11 + o12 + o13 + o14 + o15 + o16 + o17 + o18 + o19 + o20 + o21 + o22 + o23 + o24 + o25) * 100) / no
                               
    entry_progress = fields.Float(compute='_entry_progress', default=0.0, string='إكتمال الملف', store=True, tracking=True)
    
    count = fields.Integer("العدد", default=1)
    is_draft = fields.Integer(string='مسودة', compute='_get_state_numbers', store=True)
    is_confirm = fields.Integer(string='بإنتظار موافقة المدير', compute='_get_state_numbers', store=True)
    is_suspended = fields.Integer(string='معلقة', compute='_get_state_numbers', store=True)
    is_approve = fields.Integer(string='لدى العميل', compute='_get_state_numbers', store=True)
    is_refuse = fields.Integer(string='مرفوضة', compute='_get_state_numbers', store=True)
    is_close = fields.Integer(string='مغلقة', compute='_get_state_numbers', store=True)
        
    @api.depends('state')
    def _get_state_numbers(self):
        for litigation in self:
            is_draft = 0
            is_confirm = 0
            is_suspended = 0
            is_approve = 0
            is_refuse = 0
            is_close = 0
            if litigation.state == 'draft':
                is_draft = 1
            if litigation.state == 'confirm':
                is_confirm = 1
            if litigation.state == 'suspended':
                is_suspended = 1
            if litigation.state == 'Approve':
                is_approve = 1
            if litigation.state == 'Refuse':
                is_refuse = 1
            if litigation.state == 'close':
                is_close = 1
            litigation.is_draft = is_draft
            litigation.is_confirm = is_confirm
            litigation.is_suspended = is_suspended
            litigation.is_approve = is_approve
            litigation.is_refuse = is_refuse
            litigation.is_close = is_close


    personal_status_type = fields.Many2one('personal.status.type', string='الأحوال الشخصية', auto_join=True)
    penal_type = fields.Many2one('penal.type', string='الجزائية', auto_join=True)
    execute_type = fields.Many2one('execute.type', string='التنفيذية', auto_join=True)
    general_type = fields.Many2one('general.type', string='العامة', auto_join=True)
    labor_type = fields.Many2one('labor.type', string='العمالية', auto_join=True)
    commercial_type = fields.Many2one('commercial.type', string='التجارية', auto_join=True)


    @api.model_create_multi
    def create(self, vals_list):
        record = super(litigation, self).create(vals_list)
        if record.user_id != self.env.user:
            base_url = record.company_id.website
            url = base_url + '/web#id=%s&model=litigation.litigation&view_type=form' % str(record.id)
            body_html = ("تم تعيينك على قضية " + record.name + " نأمل منكم البدأ بها " + '<div>.</div>' + '<a href="%s"style="padding: 8px 16px 8px 16px; border-radius: 3px; background-color:#875A7B; text-align:center; text-decoration:none; color: #FFFFFF;">للإطلاع</a>' % url)
            vals = {
                'subject': (" تم تعيينك على قضية" + record.name),
                'body_html': body_html,
                'author_id': record.user_id.partner_id.id,
                'email_from': record.user_id.company_id.partner_id.email_formatted or record.user_id.email_formatted,
                'email_to': record.user_id.partner_id.email,
                'auto_delete': True,
                'state': 'outgoing'
            }
            self.env['mail.mail'].sudo().create(vals).send()
        return record
        
        
class request(models.Model):
    _name = 'litigation.requests'
    _description = 'طلبات الدعوى'
       
    litigation_id = fields.Many2one('litigation.litigation', string='القضية')
    name = fields.Text("الطلب", required=True)
        
class arguments(models.Model):
    _name = 'litigation.arguments'
    _description = 'اسانيد الدعوى'

    litigation_id = fields.Many2one('litigation.litigation', string='القضية')
    name = fields.Char("الاسناد", required=True)
    url = fields.Char("الرابط", required=True)

    def _clean_url(self, url):
        url = urls.url_parse(url)
        if not url.scheme:
            if not url.netloc:
                url = url.replace(netloc=url.path, path='')
            url = url.replace(scheme='https').to_url()
        return url
    
    def write(self, vals):
        if vals.get('url'):
            vals['url'] = self._clean_url(vals['url'])
        return super(arguments, self).write(vals)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('url'):
                vals['url'] = self._clean_url(vals['url'])
        return super(arguments, self).create(vals_list)
        
class notes(models.Model):
    _name = 'litigation.notes'
    _description = 'مذكرات الدعوى'

    litigation_id = fields.Many2one('litigation.litigation', string='القضية')
    name = fields.Selection([
        ('المدعي', 'المدعي'),
        ('المدعى عليه', 'المدعى عليه'),
        ], string='كاتب المذكرة', default='المدعي', required=True)
    date = fields.Date(string='التاريخ', required=True)
    by = fields.Selection([
        ('جلسة', 'جلسة'),
        ('تبادل إلكتروني', 'تبادل إلكتروني'),
        ('أخرى', 'أخرى'),
        ], string='طريقة الاستلام', default='جلسة', required=True)
    file = fields.Binary(string='الملف', required=True)
        
class report(models.Model):
    _name = 'litigation.report'
    _description = 'تقارير الجلسات'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = 'court_date asc'
    
    url = fields.Char(compute='get_url')
    
    def get_url(self):
        base_url = self.company_id.website
        self.url = base_url + '/web#id=' + str(self.id) + '&model=litigation.report&view_type=form'

    portal_url = fields.Char(compute='get_portal_url')
    
    def get_portal_url(self):
        base_url = self.company_id.website
        self.portal_url = base_url + '/my/litigation/' + str(self.litigation_id.id) + '?access_token=' + str(self.litigation_id.access_token)

    def preview_portal(self):
        self.ensure_one()
        base_url = self.company_id.website
        portal_url = base_url + '/my/report/' + str(self.id) + '?access_token={' + str(self.access_token) + "}"
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': portal_url,
        }
    
    def _default_access_token(self):
        return str(uuid.uuid4())

    access_token = fields.Char('Security Token', required=True, default=_default_access_token, readonly=True)
    
    def attachment_tree_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        action['domain'] = str([('res_model', '=', 'litigation.report'),('res_id', 'in', self.ids),])
        action['context'] = "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        return action
    
    def _compute_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'litigation.report'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = { res['res_id']: res['res_id_count'] for res in read_group_res }
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)
    
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_confirm(self):
        self.write({'state': 'confirm'})
        notification_ids = []
        for report in self:
            if report.lawyer_manager.user_id.id:
                notification_ids.append((0,0,{
                'res_partner_id':report.lawyer_manager.user_id.partner_id.id,
                'notification_type':'inbox'}))
            report.message_post(
                subject="اعتماد",
                body= "تم تقديم طلب الاعتماد، نأمل منكم الإطلاع والتعميد",
                message_type='notification',
                notification_ids=notification_ids,
               )
        if report.user_id:
            report.message_subscribe(partner_ids=report.user_id.partner_id.ids)
        if report.partner_id:
            report.message_subscribe(partner_ids=report.partner_id.ids)
        if report.parent_id:
            report.message_subscribe(partner_ids=report.parent_id.ids)
        return True

    def action_refuse(self):
        self.write({'state': 'Refuse'})
        notification_ids = []
        for report in self:
            if report.lawyer_manager.user_id.id:
                notification_ids.append((0,0,{
                'res_partner_id':report.user_id.partner_id.id,
                'notification_type':'inbox'}))
            report.message_post(
                subject="رفض",
                body= "تم إعادة التقرير. نأمل منكم مراجعته وإعادة تقديم طلب الاعتماد",
                message_type='notification',
                notification_ids=notification_ids,
               )
        return True

    def action_suspended(self):
        self.write({'state': 'suspended'})
        return True
    
    def action_pull(self):
        self.write({'state': 'confirm'})
        return True

    def action_approve(self):
        self.write({'state': 'Approve'})
        notification_ids = []
        for report in self:
            if report.lawyer_manager.user_id.id:
                if self.env.user.id != report.lawyer_manager.user_id.id:
                    notification_ids.append((0,0,{
                    'res_partner_id':report.lawyer_manager.user_id.partner_id.id,
                    'notification_type':'inbox'}))
                report.message_post(
                    subject="موافقة",
                    body= ("تمت الموافقة على التقرير من قبل " + self.env.user.name),
                    message_type='notification',
                    notification_ids=notification_ids,
                   )
            if report.litigation_id.partner_id_emails:
                mail_template = self.env.ref('litigation.send_litigation_partner')
                mail_template.send_mail(report.litigation_id.id, force_send=True,notif_layout='mail.mail_notification_light')
        return True

    def action_close(self):
        self.write({'state': 'close'})
        return True
    
    system_user = fields.Char(compute='_get_system_user')
    
    def _get_system_user(self):
        for litigation in self:
            if litigation.env.user.has_group('base.group_system'):
                litigation.system_user = 'True'
            else:
                litigation.system_user = 'False'
    
    current_user = fields.Char(compute='_get_current_user')
                    
    def _get_current_user(self):
        for report in self:
            if report.env.user.id == report.user_id.id:
                if report.user_id.lawyer_manager:
                    report.current_user = 'False'
                elif report.env.user.id == report.user_id.lawyer_manager:
                    report.current_user = 'True'
                else:
                    report.current_user = 'True'
            elif report.env.user.has_group('litigation.group_law_lawyer_manager'):
                report.current_user = 'True'
            else:
                report.current_user = 'False'

    lawyer_manager = fields.Many2one('res.users', string='المدير المحامي', compute='_get_lawyer_manager')

    def _get_lawyer_manager(self):
        for report in self:
            lawyer_manager = report.user_id.id
            if report.user_id.lawyer_manager:
                lawyer_manager = report.user_id.lawyer_manager
            report.lawyer_manager = lawyer_manager
            
    @api.depends('litigation_id.partner_id','litigation_id.user_id')
    def _get_partner_user(self):
        for litigation in self:
            partner_id = False
            user_id = self.env.user.id
            if litigation.litigation_id.partner_id:
                partner_id = litigation.litigation_id.partner_id.id
            if litigation.litigation_id.user_id:
                user_id = litigation.litigation_id.user_id.id
            litigation.partner_id = partner_id
            litigation.user_id = user_id



    name = fields.Char("الجلسة", tracking=True)
    litigation_id = fields.Many2one('litigation.litigation', string='القضية', readonly=False, index=True, tracking=True)
    company_id = fields.Many2one('res.company', related='user_id.company_id', string='Company', required=True)
    user_id = fields.Many2one('res.users', compute='_get_partner_user', string='المحامي', tracking=True, store=True)
    helper_ids = fields.Many2many(related='litigation_id.helper_ids')
    partner_id = fields.Many2one('res.partner', compute='_get_partner_user', string='العميل', tracking=True, store=True)
    parent_id = fields.Many2one('res.partner', related='partner_id.parent_id', string='شركة العميل', auto_join=True)
    full_permission = fields.Many2many(related='partner_id.full_permission')
    manager_permission = fields.Many2many(related='partner_id.manager_permission')
    next_court_date = fields.Datetime(string='موعد الجلسة القادمة', index=True, copy=False, tracking=True)
    court_date = fields.Datetime(string='تاريخ الجلسة', index=True, copy=False, tracking=True)
    present_judges = fields.Text(string='القضاة الحاضرين', index=True, tracking=True)
    writer = fields.Char(string='أمين السر / الكاتب', index=True, tracking=True)
    link = fields.Char(string='للاطلاع على المستندات', index=True, tracking=True)
    summary = fields.Text(string='ضبط الجلسة', tracking=True)
    task_ids = fields.One2many('project.task', 'report_id', string='الطلبات')
    attachment_number = fields.Integer(compute='_compute_attachment_number', string="Number of Attachments")
    court_type = fields.Selection([
        ('عن بعد', 'عن بعد'),
        ('مباشرة', 'مباشرة')
        ], string='نوع الجلسة', store=True, copy=False, readonly=False, tracking=True)
    online_type = fields.Selection([
        ('كتابية', 'كتابية'),
        ('مرئية', 'مرئية')
        ], string='نوعها', store=True, copy=False, readonly=False, tracking=True)
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('confirm', 'بإنتظار موافقة المدير'),
        ('suspended', 'معلقة'),
        ('Approve', 'لدى العميل'),
        ('Refuse', 'مرفوضة'),
        ('close', 'مغلقة')
        ], string='الإجراءات الداخلية', store=True, copy=False, readonly=False, default='draft')
    
    @api.depends('name','litigation_id','next_court_date','court_date','present_judges','writer','summary','court_type')
    def _entry_progress(self):
        for report in self:
            o1 = 0          
            o2 = 0          
            o3 = 0         
            o4 = 0  
            o5 = 0
            o6 = 0        
            o7 = 0          
            o8 = 0           
            o9 = 0           
            no = 8
            if report.name:
                o1 = 1
            if report.litigation_id:
                o2 = 1
            if report.next_court_date:
                o3 = 1
            if report.court_date:
                o4 = 1
            if report.present_judges:
                o5 = 1
            if report.writer:
                o6 = 1
            if report.summary:
                o7 = 1
            if report.court_type:
                o8 = 1
                if report.court_type == 'عن بعد':
                    no = 9
                    if report.online_type:
                        o9 = 1
                
        report.entry_progress = ((o1 + o2 + o3 + o4 + o5 + o6 + o7 + o8 + o9) * 100) / no

    entry_progress = fields.Float(compute='_entry_progress', default=0.0, string='إكتمال الملف', store=True, tracking=True)
    
    
    
class Attorney(models.Model):
    _name = 'attorney.attorney'
    _description = 'الوكالات'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = 'expiration'

    url = fields.Char(compute='get_url')
    
    def get_url(self):
        for attorney in self:
            base_url = attorney.company_id.website
            attorney.url = base_url + '/web#id=' + str(attorney.id) + '&model=attorney.attorney&view_type=form'

    name = fields.Char("الوكالة", compute='_compute_name', readonly=False, store=True)
    
    @api.depends('partner_id') 
    def _compute_name(self):
        for attorney in self:
            if attorney.partner_id:
                attorney.name = 'وكالة ' + attorney.partner_id.name
            else:
                attorney.name = False
                
    user_id = fields.Many2one('res.users', string='الوكيل', default=lambda self: self.env.user, required=True)
    partner_id = fields.Many2one('res.partner', string='الموكل', auto_join=True, required=True)
    company_id = fields.Many2one(related='user_id.company_id')
    attorney_date = fields.Date(string='تاريخ الوكالة', index=True, copy=False, required=True)
    ending_date = fields.Date(string='تاريخ إنتهاء الوكالة', index=True, copy=False, required=True)
    number = fields.Char(string='رقم الوكالة')
    source = fields.Char(string='مصدر الوكالة')
    file = fields.Binary(string='ملف الوكالة')
    attorney_status = fields.Selection([
        ('مباشرة', 'مباشرة'),
        ('غير مباشرة', 'غير مباشرة')
        ], string='صفة الوكالة', store=True, copy=False, default='مباشرة')
    client_state = fields.Selection([
            ('أصالة عن نفسه', 'أصالة عن نفسه'),
            ('صاحب مؤسسة', 'صاحب مؤسسة'),
            ('صاحب مكتب', 'صاحب مكتب'),
            ('ممثل شركة', 'ممثل شركة'),
            ('مصفى شركة', 'مصفى شركة'),
            ('ولي على قاصر', 'ولي على قاصر'),
            ('ناظر على وقف', 'ناظر على وقف'),
            ('ممثل نشأة', 'ممثل نشأة'),
            ('أمين عام', 'أمين عام'),
            ('حارس قضائي', 'حارس قضائي'),
            ('وكالة من خارج النظام', 'وكالة من خارج النظام'),
            ('وكيل بموجب وكالة', 'وكيل بموجب وكالة'),
            ('مدير الشركة', 'مدير الشركة'),
            ('رئيس مجلس الإدارة', 'رئيس مجلس الإدارة'),
            ], string='صفة الموكل', store=True, copy=False)
    lawyer_state = fields.Selection([
            ('أصالة عن نفسه', 'أصالة عن نفسه'),
            ('صاحب مؤسسة', 'صاحب مؤسسة'),
            ('صاحب مكتب', 'صاحب مكتب'),
            ('مدير مكتب', 'مدير مكتب'),
            ('مصفى شركة', 'مصفى شركة'),
            ('ولي على قاصر', 'ولي على قاصر'),
            ('ناظر على وقف', 'ناظر على وقف'),
            ('ممثل نشأة', 'ممثل نشأة'),
            ('شريك في الشركة', 'شريك في الشركة'),
            ], string='صفة الوكيل', store=True, copy=False, readonly=False)
    origin = fields.Many2one('res.partner', string='الموكل من الأصيل', auto_join=True)
    attorney_origin_date = fields.Date(string='تاريخ وكالة الأصيل', index=True, copy=False)
    number_origin = fields.Char(string='رقم وكالة الأصيل')
    expiration = fields.Selection([
        ('جديدة', 'جديدة'),
        ('سارية', 'سارية'),
        ('قاربت على الإنتهاء', 'قاربت على الإنتهاء'),
        ('منتهية', 'منتهية'),
        ('مجددة', 'مجددة'),
        ], string='حالة الوكالة', store=True, default='جديدة')
    
    late_attorney_id = fields.Many2one('attorney.attorney', compute='_get_late_attorney_id')

    def _get_late_attorney_id(self):
        for attorney in self:
            late_attorney_ids = self.env['attorney.attorney'].search([('partner_id','=', attorney.partner_id.id),('ending_date','>=', attorney.attorney_date)], limit=1)
            if late_attorney_ids:
                attorney.late_attorney_id = late_attorney_ids.id
            else:
                attorney.late_attorney_id = False

    new_attorney_id = fields.Many2one('attorney.attorney', compute='_get_new_attorney_id')

    def _get_new_attorney_id(self):
        for attorney in self:
            new_attorney_ids = self.env['attorney.attorney'].search([('partner_id','=', attorney.partner_id.id),('ending_date','<=', attorney.attorney_date)], limit=1)
            if new_attorney_ids:
                attorney.new_attorney_id = new_attorney_ids.id
            else:
                attorney.new_attorney_id = False


    def _get_expiration(self):
        attorney_ids = self.env['attorney.attorney'].search([])
        for attorney in attorney_ids:
            if attorney.attorney_date and attorney.ending_date:
                today = datetime.today().date()
                days_remaining = attorney.ending_date - today
                remaining_days = days_remaining.days
                if attorney.new_attorney_id:
                    attorney.expiration = 'مجددة'
                elif remaining_days <= 30 and remaining_days > 0:
                    attorney.expiration = 'قاربت على الإنتهاء'
                elif attorney.attorney_date <= today and attorney.ending_date >= today:
                    attorney.expiration = 'سارية'
                elif attorney.attorney_date <= today and attorney.ending_date <= today:
                    attorney.expiration = 'منتهية'
                else:
                    attorney.expiration = 'جديدة'
                        
    @api.constrains('ending_date')
    def _check_dates(self):
        for attorney in self:
            if attorney.attorney_date and attorney.ending_date:
                if attorney.attorney_date >= attorney.ending_date:
                    raise ValidationError(_('يجب أن يكون تاريخ الوكالة أكبر من تاريخ إنتهائها'))    

    @api.constrains('partner_id')
    def _check_attorney(self):
        for attorney in self:
            attorney_ids = self.env['attorney.attorney'].search([('partner_id','=', attorney.partner_id.id),('expiration','!=','منتهية')])
            if len(attorney_ids)>1:
                raise ValidationError(_('توجد وكالة للعميل غير منتهية الصلاحية'))
        
        
    def _ending_date_reminder(self):
        records = self.env['attorney.attorney'].search([('expiration','!=','منتهية')])
        for attorney in records:
            if not attorney.new_attorney_id:
                days_30 = attorney.ending_date - timedelta(days = 30)
                days_15 = attorney.ending_date - timedelta(days = 15)
                days_10 = attorney.ending_date - timedelta(days = 10)
                days_3 = attorney.ending_date - timedelta(days = 3)
                day_1 = attorney.ending_date - timedelta(days = 1)
                today = datetime.today().date()
                if day_1 == today or days_3 == today or days_10 == today or days_15 == today or days_30 == today:
                    if days_30 == today:
                        subject = ("تبقى على إنتهاء وكالة " + attorney.partner_id.name + " شهر واحد")
                    elif days_15 == today:
                        subject = ("تبقى على إنتهاء وكالة " + attorney.partner_id.name + " 15 يوم")
                    elif days_10 == today:
                        subject = ("تبقى على إنتهاء وكالة " + attorney.partner_id.name + " 10 أيام")
                        value = {
                            'summary': ('تجديد وكالة ' + attorney.partner_id.name),
                            'activity_type_id': self.env['mail.activity.type'].search([('id', '=', 4)], limit=1).id,
                            'res_model_id': self.env['ir.model'].search([('model', '=', 'attorney.attorney')], limit=1).id,
                            'automated': True,
                            'res_id': attorney.id,
                            'user_id': attorney.user_id.id,
                            'date_deadline': attorney.ending_date,
                        }
                        self.env['mail.activity'].sudo().create(value)
                        if attorney.user_id.lawyer_manager:
                            lawyer_manager_value = {
                                'summary': ('تجديد وكالة ' + attorney.partner_id.name),
                                'activity_type_id': self.env['mail.activity.type'].search([('id', '=', 4)], limit=1).id,
                                'res_model_id': self.env['ir.model'].search([('model', '=', 'attorney.attorney')], limit=1).id,
                                'automated': True,
                                'res_id': attorney.id,
                                'user_id': attorney.user_id.lawyer_manager.id,
                                'date_deadline': attorney.ending_date,
                            }
                            self.env['mail.activity'].sudo().create(lawyer_manager_value)

                    elif days_3 == today:
                        subject = ("تبقى على إنتهاء وكالة " + attorney.partner_id.name + " 3 أيام")
                    elif day_1 == today:
                        subject = ("تبقى على إنتهاء وكالة " + attorney.partner_id.name + " يوم واحد")
                    body_html = ("وكالة " + attorney.partner_id.name + " على وشك الإنتهاء، نأمل منكم تجديدها")
                    vals = {
                        'subject': subject,
                        'body_html': body_html,
                        'author_id': attorney.user_id.partner_id.id,
                        'email_from': attorney.user_id.company_id.partner_id.email_formatted or attorney.user_id.email_formatted,
                        'email_to': attorney.user_id.partner_id.email,
                        'auto_delete': True,
                        'state': 'outgoing'
                    }
                    self.env['mail.mail'].sudo().create(vals).send()
                    
class consulting(models.Model):
    _name = 'consulting.consulting'
    _description = 'الاستشارات'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = 'id'
        
        
    partner_id_emails = fields.Char(compute='get_partner_id_emails')

    def get_partner_id_emails(self):
        for consulting in self:
            full_permission_email = ''
            full_permission_emails = ''
            for full_permission in consulting.partner_id.full_permission:
                full_permission_email += full_permission.partner_id.email + ','
            full_permission_emails += full_permission_email
            if consulting.partner_id.email:
                partner_email = consulting.partner_id.email
            full_emails = full_permission_emails + partner_email
            consulting.partner_id_emails = full_emails

        
    url = fields.Char(compute='get_url')
    
    def get_url(self):
        base_url = self.company_id.website
        self.url = base_url + '/web#id=' + str(self.id) + '&model=consulting.consulting&view_type=form'

    portal_url = fields.Char(compute='get_portal_url')
    
    def get_portal_url(self):
        base_url = self.company_id.website
        self.portal_url = base_url + '/my/consulting/' + str(self.id) + '?access_token=' + str(self.access_token)
        
        
    def get_portal_url_pdf_download(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        self.ensure_one()
        base_url = self.company_id.website
        access_url = base_url + '/my/consulting_print/' + str(self.id)
        url = access_url + '%s?access_token=%s%s%s%s%s' % (
            suffix if suffix else '',
            self.access_token,
            '&report_type=%s' % report_type if report_type else '',
            '&download=true' if download else '',
            query_string if query_string else '',
            '#%s' % anchor if anchor else ''
        )
        return url

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s' % (self.name)    
    
    def preview_portal(self):
        self.ensure_one()
        base_url = self.company_id.website
        portal_url = base_url + '/my/consulting/' + str(self.id) + '?access_token={' + str(self.access_token) + "}"
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': portal_url,
        }
    
    def _default_access_token(self):
        return str(uuid.uuid4())

    access_token = fields.Char('Security Token', required=True, default=_default_access_token, readonly=True)
        
    def attachment_tree_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        action['domain'] = str([('res_model', '=', 'consulting.consulting'),('res_id', 'in', self.ids),])
        action['context'] = "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        return action
    
    def _compute_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'consulting.consulting'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = { res['res_id']: res['res_id_count'] for res in read_group_res }
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)
    
        
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_confirm(self):
        self.write({'state': 'confirm'})
        notification_ids = []
        for consulting in self:
            if consulting.lawyer_manager.user_id.id:
                notification_ids.append((0,0,{
                'res_partner_id':consulting.lawyer_manager.user_id.partner_id.id,
                'notification_type':'inbox'}))
            consulting.message_post(
                subject="اعتماد",
                body= "تم تقديم طلب الاعتماد، نأمل منكم الإطلاع والتعميد",
                message_type='notification',
                notification_ids=notification_ids,
               )
        if consulting.user_id:
            consulting.message_subscribe(partner_ids=consulting.user_id.partner_id.ids)
        if consulting.partner_id:
            consulting.message_subscribe(partner_ids=consulting.partner_id.ids)
        if consulting.parent_id:
            consulting.message_subscribe(partner_ids=consulting.parent_id.ids)
        return True

    def action_refuse(self):
        self.write({'state': 'Refuse'})
        notification_ids = []
        for consulting in self:
            if consulting.lawyer_manager.user_id.id:
                notification_ids.append((0,0,{
                'res_partner_id':consulting.user_id.partner_id.id,
                'notification_type':'inbox'}))
            consulting.message_post(
                subject="رفض",
                body= "تم إعادة الاستشارة. نأمل منكم مراجعتها وإعادة تقديم طلب الاعتماد",
                message_type='notification',
                notification_ids=notification_ids,
               )
        return True

    def action_suspended(self):
        self.write({'state': 'suspended'})
        return True
    
    def action_pull(self):
        self.write({'state': 'confirm'})
        return True

    def action_approve(self):
        self.write({'state': 'Approve'})
        notification_ids = []
        for consulting in self:
            consulting.served_date = fields.datetime.now()
            if consulting.lawyer_manager.user_id.id:
                if self.env.user.id != consulting.lawyer_manager.user_id.id:
                    notification_ids.append((0,0,{
                    'res_partner_id':consulting.lawyer_manager.user_id.partner_id.id,
                    'notification_type':'inbox'}))
                consulting.message_post(
                    subject="موافقة",
                    body= ("تمت الموافقة على الاستشارة من قبل " + self.env.user.name),
                    message_type='notification',
                    notification_ids=notification_ids,
                   )
            if consulting.partner_id_emails:
                mail_template = self.env.ref('litigation.send_consulting_partner')
                mail_template.send_mail(consulting.id, force_send=True,notif_layout='mail.mail_notification_light')
        return True

    def action_close(self):
        self.write({'state': 'close'})
        return True
    
    system_user = fields.Char(compute='_get_system_user')
    
    def _get_system_user(self):
        for litigation in self:
            if litigation.env.user.has_group('base.group_system'):
                litigation.system_user = 'True'
            else:
                litigation.system_user = 'False'

    current_user = fields.Char(compute='_get_current_user')  

    def _get_current_user(self):
        for consulting in self:
            if consulting.env.user.id == consulting.user_id.id:
                if consulting.user_id.lawyer_manager:
                    consulting.current_user = 'False'
                elif consulting.env.user.id == consulting.user_id.lawyer_manager:
                    consulting.current_user = 'True'
                else:
                    consulting.current_user = 'True'
            elif consulting.env.user.has_group('litigation.group_law_consultant_manager'):
                consulting.current_user = 'True'
            else:
                consulting.current_user = 'False'

            
    lawyer_manager = fields.Many2one('res.users', string='المدير المحامي', compute='_get_lawyer_manager')

    def _get_lawyer_manager(self):
        for consulting in self:
            lawyer_manager = consulting.user_id.id
            if consulting.user_id.lawyer_manager:
                lawyer_manager = consulting.user_id.lawyer_manager
            consulting.lawyer_manager = lawyer_manager

                        
    @api.depends('project_id.user_id')
    def _get_partner_user(self):
        for consulting in self:
            user_id = self.env.user.id
            if consulting.project_id.user_id:
                user_id = consulting.project_id.user_id.id
            consulting.user_id = user_id
            
    @api.depends('project_prt')
    def _get_partner_id(self):
        for consulting in self:
            consulting.partner_id = consulting.project_prt

            
    name = fields.Char("الاستشارة", tracking=True)
    partner_id = fields.Many2one('res.partner', string='العميل', compute='_get_partner_id', auto_join=True, tracking=True, store=True, readonly=False)
    project_prt = fields.Many2one(related='project_id.partner_id')
    parent_id = fields.Many2one('res.partner', related='partner_id.parent_id', string='شركة العميل', auto_join=True)
    full_permission = fields.Many2many(related='partner_id.full_permission')
    manager_permission = fields.Many2many(related='partner_id.manager_permission')
    company_id = fields.Many2one('res.company', related='user_id.company_id', string='Company', required=True)
    project_id = fields.Many2one('project.project', string='المشروع', store=True, readonly=False, index=True, change_default=True, tracking=True)
    user_id = fields.Many2one('res.users', compute='_get_partner_user', string='المستشار', tracking=True, store=True)
    helper = fields.Boolean(string='الاستشارة تحتاج مساعد')
    helper_ids = fields.Many2many(string='مساعد المستشار', related='project_id.helper_ids')
    date = fields.Datetime(string='تاريخ الاستشارة', index=True, copy=False, tracking=True)
    summary = fields.Text(string='ملخص استشارة العميل', tracking=True)
    consult = fields.Text(string='الرأي الاستشاري المقترح', tracking=True)
    task_ids = fields.One2many('project.task', 'consulting_id', string='المهام')
    attachment_number = fields.Integer(compute='_compute_attachment_number', string="Number of Attachments")
    other = fields.Char(string='اخرى', index=True, tracking=True)
    consulting_type = fields.Selection([
            ('استشارة أحوال شخصية', 'استشارة أحوال شخصية'),
            ('دراسة قضية', 'دراسة قضية'),
            ('استشارة تأمينية', 'استشارة تأمينية'),
            ('استشارة مصرفية', 'استشارة مصرفية'),
            ('استشارة تمويلية', 'استشارة تمويلية'),
            ('استشارة جنائية', 'استشارة جنائية'),
            ('استشارة إدارية', 'استشارة إدارية'),
            ('استشارة عمالية', 'استشارة عمالية'),
            ('استشارة تجارية', 'استشارة تجارية'),
            ('استشارة أوقاف', 'استشارة أوقاف'),
            ('استشارة قانونية أخرى', 'استشارة قانونية أخرى')
            ], string='نوع الاستشارة', store=True, copy=False, readonly=False, tracking=True)
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('confirm', 'بإنتظار موافقة المدير'),
        ('suspended', 'معلقة'),
        ('Approve', 'لدى العميل'),
        ('Refuse', 'مرفوضة'),
        ('close', 'مغلقة')
        ], string='الإجراءات الداخلية', store=True, copy=False, readonly=False, default='draft')
    service_standard = fields.Selection([
        ('غير معقد', 'غير معقد'),
        ('متوسطة التعقيد', 'متوسطة التعقيد'),
        ('عالي التعقيد', 'عالي التعقيد'),
        ], string='معيار الخدمة', store=True, copy=False)
    customer_rating = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], default='0', index=True, string="تقييم العميل", tracking=True)
    customer_response=fields.Text("ملاحظات العميل", tracking=True)

    served_date = fields.Datetime(string='تاريخ تقديم الاستشارة', tracking=True)

    @api.depends('name','partner_id','summary','consult','other','consulting_type','date')
    def _entry_progress(self):
        for consulting in self:
            o1 = 0          
            o2 = 0          
            o3 = 0         
            o4 = 0  
            o5 = 0
            o6 = 0        
            o7 = 0        
            no = 6
            if consulting.name:
                o1 = 1
            if consulting.partner_id:
                o2 = 1
            if consulting.summary:
                o3 = 1
            if consulting.consult:
                o4 = 1
            if consulting.consulting_type:
                o5 = 1
            if consulting.consulting_type == 'استشارة قانونية أخرى':
                no = 7
                if consulting.other:
                    o6 = 1
            if consulting.date:
                o7 = 1
        consulting.entry_progress = ((o1 + o2 + o3 + o4 + o5 + o6 + o7) * 100) / no

    entry_progress = fields.Float(compute='_entry_progress', default=0.0, string='إكتمال الملف', store=True, tracking=True)
            
    count = fields.Integer("العدد", default=1)
    is_draft = fields.Integer(string='مسودة', compute='_get_state_numbers', store=True)
    is_confirm = fields.Integer(string='بإنتظار موافقة المدير', compute='_get_state_numbers', store=True)
    is_suspended = fields.Integer(string='معلقة', compute='_get_state_numbers', store=True)
    is_approve = fields.Integer(string='لدى العميل', compute='_get_state_numbers', store=True)
    is_refuse = fields.Integer(string='مرفوضة', compute='_get_state_numbers', store=True)
    is_close = fields.Integer(string='مغلقة', compute='_get_state_numbers', store=True)
    
    @api.depends('state')
    def _get_state_numbers(self):
        for consulting in self:
            is_draft = 0
            is_confirm = 0
            is_suspended = 0
            is_approve = 0
            is_refuse = 0
            is_close = 0
            if consulting.state == 'draft':
                is_draft = 1
            if consulting.state == 'confirm':
                is_confirm = 1
            if consulting.state == 'suspended':
                is_suspended = 1
            if consulting.state == 'Approve':
                is_approve = 1
            if consulting.state == 'Refuse':
                is_refuse = 1
            if consulting.state == 'close':
                is_close = 1
            consulting.is_draft = is_draft
            consulting.is_confirm = is_confirm
            consulting.is_suspended = is_suspended
            consulting.is_approve = is_approve
            consulting.is_refuse = is_refuse
            consulting.is_close = is_close

    @api.model_create_multi
    def create(self, vals_list):
        record = super(consulting, self).create(vals_list)
        if record.user_id != self.env.user:
            base_url = record.company_id.website
            url = base_url + '/web#id=%s&model=consulting.consulting&view_type=form' % str(record.id)
            body_html = ("تم تعيينك على استشارة " + record.name + " نأمل منكم البدأ بها " + '<div>.</div>' + '<a href="%s"style="padding: 8px 16px 8px 16px; border-radius: 3px; background-color:#875A7B; text-align:center; text-decoration:none; color: #FFFFFF;">للإطلاع</a>' % url)
            vals = {
                'subject': (" تم تعيينك على استشارة" + record.name),
                'body_html': body_html,
                'author_id': record.user_id.partner_id.id,
                'email_from': record.user_id.company_id.partner_id.email_formatted or record.user_id.email_formatted,
                'email_to': record.user_id.partner_id.email,
                'auto_delete': True,
                'state': 'outgoing'
            }
            self.env['mail.mail'].sudo().create(vals).send()
        return record        
        
class contractconsulting(models.Model):
    _name = 'contractconsulting.contractconsulting'
    _description = 'استشارات العقود'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = 'id'
    
    partner_id_emails = fields.Char(compute='get_partner_id_emails')

    def get_partner_id_emails(self):
        for consulting in self:
            full_permission_email = ''
            full_permission_emails = ''
            for full_permission in consulting.partner_id.full_permission:
                full_permission_email += full_permission.partner_id.email + ','
            full_permission_emails += full_permission_email
            if consulting.partner_id.email:
                partner_email = consulting.partner_id.email
            full_emails = full_permission_emails + partner_email
            consulting.partner_id_emails = full_emails

    url = fields.Char(compute='get_url')
    
    def get_url(self):
        base_url = self.company_id.website
        self.url = base_url + '/web#id=' + str(self.id) + '&model=contractconsulting.contractconsulting&view_type=form'

    
    portal_url = fields.Char(compute='get_portal_url')
    
    def get_portal_url(self):
        base_url = self.company_id.website
        self.portal_url = base_url + '/my/contractconsulting/' + str(self.id) + '?access_token=' + str(self.access_token)
        
        
    def preview_portal(self):
        self.ensure_one()
        base_url = self.company_id.website
        portal_url = base_url + '/my/contractconsulting/' + str(self.id) + '?access_token={' + str(self.access_token) + "}"
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': portal_url,
        }
    
    
    def _default_access_token(self):
        return str(uuid.uuid4())

    access_token = fields.Char('Security Token', required=True, default=_default_access_token, readonly=True)
                
    def attachment_tree_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        action['domain'] = str([('res_model', '=', 'contractconsulting.contractconsulting'),('res_id', 'in', self.ids),])
        action['context'] = "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        return action

    
    def _compute_attachment_number(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'contractconsulting.contractconsulting'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = { res['res_id']: res['res_id_count'] for res in read_group_res }
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)
    
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_confirm(self):
        self.write({'state': 'confirm'})
        notification_ids = []
        for contractconsulting in self:
            if contractconsulting.lawyer_manager.user_id.id:
                notification_ids.append((0,0,{
                'res_partner_id':contractconsulting.lawyer_manager.user_id.partner_id.id,
                'notification_type':'inbox'}))
            contractconsulting.message_post(
                subject="اعتماد",
                body= "تم تقديم طلب الاعتماد، نأمل منكم الإطلاع والتعميد",
                message_type='notification',
                notification_ids=notification_ids,
               )
        if contractconsulting.user_id:
            contractconsulting.message_subscribe(partner_ids=contractconsulting.user_id.partner_id.ids)
        if contractconsulting.partner_id:
            contractconsulting.message_subscribe(partner_ids=contractconsulting.partner_id.ids)
        if contractconsulting.parent_id:
            contractconsulting.message_subscribe(partner_ids=contractconsulting.parent_id.ids)
        return True

    def action_refuse(self):
        self.write({'state': 'Refuse'})
        notification_ids = []
        for contractconsulting in self:
            if contractconsulting.lawyer_manager.user_id.id:
                notification_ids.append((0,0,{
                'res_partner_id':contractconsulting.user_id.partner_id.id,
                'notification_type':'inbox'}))
            contractconsulting.message_post(
                subject="رفض",
                body= "تم إعادة الاستشارة. نأمل منكم مراجعتها وإعادة تقديم طلب الاعتماد",
                message_type='notification',
                notification_ids=notification_ids,
               )
        return True

    def action_suspended(self):
        self.write({'state': 'suspended'})
        return True
    
    def action_pull(self):
        self.write({'state': 'confirm'})
        return True

    def action_approve(self):
        self.write({'state': 'Approve'})
        notification_ids = []
        for contractconsulting in self:
            contractconsulting.served_date = fields.datetime.now()
            if contractconsulting.lawyer_manager.user_id.id:
                if self.env.user.id != contractconsulting.lawyer_manager.user_id.id:
                    notification_ids.append((0,0,{
                    'res_partner_id':contractconsulting.lawyer_manager.user_id.partner_id.id,
                    'notification_type':'inbox'}))
                contractconsulting.message_post(
                    subject="موافقة",
                    body= ("تمت الموافقة على الاستشارة من قبل " + self.env.user.name),
                    message_type='notification',
                    notification_ids=notification_ids,
                   )
            if contractconsulting.partner_id_emails:
                mail_template = self.env.ref('litigation.send_consulting_partner')
                mail_template.send_mail(contractconsulting.id, force_send=True,notif_layout='mail.mail_notification_light')
        return True

    def action_close(self):
        self.write({'state': 'close'})
        return True

    system_user = fields.Char(compute='_get_system_user')
    
    def _get_system_user(self):
        for litigation in self:
            if litigation.env.user.has_group('base.group_system'):
                litigation.system_user = 'True'
            else:
                litigation.system_user = 'False'
    
    current_user = fields.Char(compute='_get_current_user')
    
    def _get_current_user(self):
        for consulting in self:
            if consulting.env.user.id == consulting.user_id.id:
                if consulting.user_id.lawyer_manager:
                    consulting.current_user = 'False'
                elif consulting.env.user.id == consulting.user_id.lawyer_manager:
                    consulting.current_user = 'True'
                else:
                    consulting.current_user = 'True'
            elif consulting.env.user.has_group('litigation.group_law_contractconsulting_manager'):
                consulting.current_user = 'True'
            else:
                consulting.current_user = 'False'

            
    lawyer_manager = fields.Many2one('res.users', string='المدير المحامي', compute='_get_lawyer_manager')            

    def _get_lawyer_manager(self):
        for consulting in self:
            lawyer_manager = consulting.user_id.id
            if consulting.user_id.lawyer_manager:
                lawyer_manager = consulting.user_id.lawyer_manager
            consulting.lawyer_manager = lawyer_manager
            
            
            
    @api.depends('project_id.user_id')
    def _get_partner_user(self):
        for consulting in self:
            user_id = self.env.user.id
            if consulting.project_id.user_id:
                user_id = consulting.project_id.user_id.id
            consulting.user_id = user_id
            
    @api.depends('project_prt')
    def _get_partner_id(self):
        for contractconsulting in self:
            contractconsulting.partner_id = contractconsulting.project_prt
            
    name = fields.Char("استشارة العقد", tracking=True)
    partner_id = fields.Many2one('res.partner', string='العميل', compute='_get_partner_id', auto_join=True, tracking=True, store=True, readonly=False)
    project_prt = fields.Many2one(related='project_id.partner_id')
    parent_id = fields.Many2one('res.partner', related='partner_id.parent_id', string='شركة العميل', auto_join=True)
    full_permission = fields.Many2many(related='partner_id.full_permission')
    manager_permission = fields.Many2many(related='partner_id.manager_permission')
    company_id = fields.Many2one('res.company', related='user_id.company_id', string='Company', required=True)
    project_id = fields.Many2one('project.project', string='المشروع', store=True, readonly=False, index=True, change_default=True)
    user_id = fields.Many2one('res.users', compute='_get_partner_user', string='مسؤول العقود', tracking=True, store=True)
    helper = fields.Boolean(string='الاستشارة تحتاج مساعد')
    helper_ids = fields.Many2many(string='مساعد المستشار', related='project_id.helper_ids')
    date = fields.Datetime(string='تاريخ الاستشارة', index=True, copy=False, tracking=True)
    summary = fields.Text(string='ملخص الاستشارة', tracking=True)
    task_ids = fields.One2many('project.task', 'contractconsulting_id', string='المهام')
    attachment_number = fields.Integer(compute='_compute_attachment_number', string="Number of Attachments")
    consulting_type = fields.Selection([
            ('عقد إيجار التجاري', 'عقد إيجار التجاري'),
            ('عقود العمل ( مدد )', 'عقود العمل ( مدد )'),
            ('عقود الفرنشايز', 'عقود الفرنشايز'),
            ('تأسيس شركة ذات مسؤولية محدودة', 'تأسيس شركة ذات مسؤولية محدودة'),
            ('عقد تأسيس / تحويل إلى شركة مساهمة', 'عقد تأسيس / تحويل إلى شركة مساهمة'),
            ('عقود الآجل ( Credit )', 'عقود الآجل ( Credit )'),
            ('عقد مقاولات', 'عقد مقاولات'),
            ('عقد وساطة وتسويق', 'عقد وساطة وتسويق'),
            ('أخرى', 'أخرى')
            ], string='نوع العقد', store=True, copy=False, readonly=False, tracking=True)
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('confirm', 'بإنتظار موافقة المدير'),
        ('suspended', 'معلقة'),
        ('Approve', 'لدى العميل'),
        ('Refuse', 'مرفوضة'),
        ('close', 'مغلقة')
        ], string='الإجراءات الداخلية', store=True, copy=False, readonly=False, default='draft')
    service_standard = fields.Selection([
        ('غير معقد', 'غير معقد'),
        ('متوسطة التعقيد', 'متوسطة التعقيد'),
        ('عالي التعقيد', 'عالي التعقيد'),
        ], string='معيار الخدمة', store=True, copy=False)
    first_time = fields.Boolean(string='عقد يحرر لأول مره')
    customer_rating = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ], default='0', index=True, string="تقييم العميل", tracking=True)
    customer_response=fields.Text("ملاحظات العميل", tracking=True)
    served_date = fields.Datetime(string='تاريخ تقديم الاستشارة', tracking=True)

    @api.depends('name','partner_id','summary','draft_contract','recommended_contract','consulting_type','date','sign_contract')
    def _entry_progress(self):
        for contractconsulting in self:
            o1 = 0          
            o2 = 0          
            o3 = 0         
            o4 = 0  
            o5 = 0
            o6 = 0        
            o7 = 0        
            o8 = 0        
            no = 7
            if contractconsulting.name:
                o1 = 1
            if contractconsulting.partner_id:
                o2 = 1
            if contractconsulting.summary:
                o3 = 1
            if contractconsulting.first_time:
                o4 = 1
            if contractconsulting.draft_contract:
                o4 = 1
            if contractconsulting.consulting_type:
                o5 = 1
            if contractconsulting.sign_contract:
                o6 = 1
            if contractconsulting.date:
                o7 = 1
        contractconsulting.entry_progress = ((o1 + o2 + o3 + o4 + o5 + o6 + o7) * 100) / no

    entry_progress = fields.Float(compute='_entry_progress', default=0.0, string='إكتمال الملف', store=True, tracking=True)
    
    count = fields.Integer("العدد", default=1)
    is_draft = fields.Integer(string='مسودة', compute='_get_state_numbers', store=True)
    is_confirm = fields.Integer(string='بإنتظار موافقة المدير', compute='_get_state_numbers', store=True)
    is_suspended = fields.Integer(string='معلقة', compute='_get_state_numbers', store=True)
    is_approve = fields.Integer(string='لدى العميل', compute='_get_state_numbers', store=True)
    is_refuse = fields.Integer(string='مرفوضة', compute='_get_state_numbers', store=True)
    is_close = fields.Integer(string='مغلقة', compute='_get_state_numbers', store=True)
    
    @api.depends('state')
    def _get_state_numbers(self):
        for consulting in self:
            is_draft = 0
            is_confirm = 0
            is_suspended = 0
            is_approve = 0
            is_refuse = 0
            is_close = 0
            if consulting.state == 'draft':
                is_draft = 1
            if consulting.state == 'confirm':
                is_confirm = 1
            if consulting.state == 'suspended':
                is_suspended = 1
            if consulting.state == 'Approve':
                is_approve = 1
            if consulting.state == 'Refuse':
                is_refuse = 1
            if consulting.state == 'close':
                is_close = 1
            consulting.is_draft = is_draft
            consulting.is_confirm = is_confirm
            consulting.is_suspended = is_suspended
            consulting.is_approve = is_approve
            consulting.is_refuse = is_refuse
            consulting.is_close = is_close

    draft_contract = fields.Char(string='مسودة العقد الأولية', tracking=True)
    recommended_contract = fields.Char(string="العقد الموصى به", tracking=True)
    sign_contract = fields.Char(string="العقد الموقع مع العميل", tracking=True)
    
    is_draft_contract = fields.Boolean(compute='_get_is_contract')
    is_recommended_contract = fields.Boolean(compute='_get_is_contract')
    is_sign_contract = fields.Boolean(compute='_get_is_contract')

    def _get_is_contract(self):
        for contract in self:
            if contract.draft_contract and contract.draft_contract != 'https://<p><br></p>':
                contract.is_draft_contract = True
            else:
                contract.is_draft_contract = False

            if contract.recommended_contract and contract.recommended_contract != 'https://<p><br></p>':
                contract.is_recommended_contract = True
            else:
                contract.is_recommended_contract = False

            if contract.sign_contract and contract.sign_contract != 'https://<p><br></p>':
                contract.is_sign_contract = True
            else:
                contract.is_sign_contract = False

    def check_sign_contract(self):
        contracts = self.env['contractconsulting.contractconsulting'].sudo().search([('recommended_contract','!=', ('|',(False),('https://<p><br></p>'))),('sign_contract','=', ('|',(False),('https://<p><br></p>')))])
        for contract in contracts:
            mail_template = self.env.ref('litigation.check_on_sign_contract')
            mail_template.send_mail(contract.id, force_send=True, notif_layout='mail.mail_notification_light')
            send_mail=True


    def _clean_draft_contract(self, draft_contract):
        url = urls.url_parse(draft_contract)
        if not url.scheme:
            if not url.netloc:
                url = url.replace(netloc=url.path, path='')
            draft_contract = url.replace(scheme='https').to_url()
            if draft_contract == 'https://<p><br></p>':
                draft_contract = False
        return draft_contract
    
    def _clean_recommended_contract(self, recommended_contract):
        url = urls.url_parse(recommended_contract)
        if not url.scheme:
            if not url.netloc:
                url = url.replace(netloc=url.path, path='')
            recommended_contract = url.replace(scheme='https').to_url()
            if recommended_contract == 'https://<p><br></p>':
                recommended_contract = False
        return recommended_contract
    
    def _clean_sign_contract(self, sign_contract):
        url = urls.url_parse(sign_contract)
        if not url.scheme:
            if not url.netloc:
                url = url.replace(netloc=url.path, path='')
            sign_contract = url.replace(scheme='https').to_url()
            if sign_contract == 'https://<p><br></p>':
                sign_contract = False
        return sign_contract
    
    def write(self, vals):
        if vals.get('draft_contract'):
            vals['draft_contract'] = self._clean_draft_contract(vals['draft_contract'])
        if vals.get('recommended_contract'):
            vals['recommended_contract'] = self._clean_recommended_contract(vals['recommended_contract'])
        if vals.get('sign_contract'):
            vals['sign_contract'] = self._clean_sign_contract(vals['sign_contract'])
        return super(contractconsulting, self).write(vals)
    
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('draft_contract'):
                vals['draft_contract'] = self._clean_draft_contract(vals['draft_contract'])
            if vals.get('recommended_contract'):
                vals['recommended_contract'] = self._clean_recommended_contract(vals['recommended_contract'])
            if vals.get('sign_contract'):
                vals['sign_contract'] = self._clean_sign_contract(vals['sign_contract'])
        record = super(contractconsulting, self).create(vals_list)
        if record.user_id != self.env.user:
            base_url = record.company_id.website
            url = base_url + '/web#id=%s&model=contractconsulting.contractconsulting&view_type=form' % str(record.id)
            body_html = ("تم تعيينك على استشارة " + record.name + " نأمل منكم البدأ بها " + '<div>.</div>' + '<a href="%s"style="padding: 8px 16px 8px 16px; border-radius: 3px; background-color:#875A7B; text-align:center; text-decoration:none; color: #FFFFFF;">للإطلاع</a>' % url)
            vals = {
                'subject': (" تم تعيينك على استشارة" + record.name),
                'body_html': body_html,
                'author_id': record.user_id.partner_id.id,
                'email_from': record.user_id.company_id.partner_id.email_formatted or record.user_id.email_formatted,
                'email_to': record.user_id.partner_id.email,
                'auto_delete': True,
                'state': 'outgoing'
            }
            self.env['mail.mail'].sudo().create(vals).send()
        return record       


