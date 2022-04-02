# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import timedelta, datetime
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError, UserError, ValidationError
import uuid

class HelpdeskTicketType(models.Model):
    _name = 'ticket.type.types'
    _description = 'النوع الفرعي'

    name = fields.Char('النوع')
    ticket_type_id = fields.Many2one('helpdesk.ticket.type', 'نوع التذكرة')


class HelpdeskTicketType(models.Model):
    _inherit = ['helpdesk.ticket.type']

    normal_time_taken = fields.Integer('الأيام لتقديم الخدمة العادية')
    urgent_time_taken = fields.Integer('الأيام لتقديم الخدمة المستعجلة')
    very_urgent_time_taken = fields.Integer('الأيام لتقديم الخدمة الطارئة')
    normal_tickets = fields.Integer('عدد التذاكر العادية بالشهر')
    urgent_tickets = fields.Integer('عدد التذاكر المستعجلة بالشهر')
    very_urgent_tickets = fields.Integer('عدد التذاكر الطارئة بالشهر')
    types_ids = fields.One2many('ticket.type.types', 'ticket_type_id', 'النوع الفرعي')



class partnerinfo(models.Model):
    _inherit = ['res.partner']
            
    today = fields.Date(default=datetime.today().date())
    month = fields.Date(compute='_count_month')
    
    def _count_month(self):
        for ticket in self:
                month = ticket.today - timedelta(days = 30)
                ticket.month = month
                
    contract_vimportant = fields.Integer(compute='_service_count')
    contract_important = fields.Integer(compute='_service_count')
    consultant_vimportant = fields.Integer(compute='_service_count')
    consultant_important = fields.Integer(compute='_service_count')
    
    def _service_count(self):
        if self.id:
            contract_vimportant = self.env['helpdesk.ticket'].search([('partner_id', '=', self.id),
                                                                   ('service_standard', '=', 'طارئ'),
                                                                   ('ticket_type_id.name', '=', 'عقد'),
                                                                   ('create_date', '<=', self.today),
                                                                   ('create_date', '>=', self.month)])
            contract_vimportants = str(len(contract_vimportant))
            self.contract_vimportant = contract_vimportants
            
            contract_important = self.env['helpdesk.ticket'].search([('partner_id', '=', self.id),
                                                                   ('service_standard', '=', 'مستعجل'),
                                                                   ('ticket_type_id.name', '=', 'عقد'),
                                                                   ('create_date', '<=', self.today),
                                                                   ('create_date', '>=', self.month)])
            contract_importants = str(len(contract_important))
            self.contract_important = contract_importants
            
            consultant_vimportant = self.env['helpdesk.ticket'].search([('partner_id', '=', self.id),
                                                                   ('service_standard', '=', 'طارئ'),
                                                                   ('ticket_type_id.name', '=', 'استشارة'),
                                                                   ('create_date', '<=', self.today),
                                                                   ('create_date', '>=', self.month)])
            consultant_vimportants = str(len(consultant_vimportant))
            self.consultant_vimportant = consultant_vimportants
            
            consultant_important = self.env['helpdesk.ticket'].search([('partner_id', '=', self.id),
                                                                   ('service_standard', '=', 'مستعجل'),
                                                                   ('ticket_type_id.name', '=', 'استشارة'),
                                                                   ('create_date', '<=', self.today),
                                                                   ('create_date', '>=', self.month)])
            consultant_importants = str(len(consultant_important))
            self.consultant_important = consultant_importants
        else:
            self.contract_vimportant = 0
            self.contract_important = 0
            self.consultant_vimportant = 0
            self.consultant_important = 0
                
    left_normal = fields.Char(default='∞')
    contractleft_vimportant = fields.Integer(compute='_service_left', string='العقود الطارئة المتبقية')
    contractleft_important = fields.Integer(compute='_service_left', string='العقود المستعجلة المتبقية')
    consultantleft_vimportant = fields.Integer(compute='_service_left', string='الاستشارات الطارئة المتبقية')
    consultantleft_important = fields.Integer(compute='_service_left', string='الاستشارات المستعجلة المتبقية')
    
    def _service_left(self):
        if self.id:
            self.contractleft_vimportant = 3 - self.contract_vimportant
            self.contractleft_important = 5 - self.contract_important
            self.consultantleft_vimportant = 3 - self.consultant_vimportant
            self.consultantleft_important = 5 - self.consultant_important
        else:
            self.contractleft_vimportant = 0
            self.contractleft_important = 0
            self.consultantleft_vimportant = 0
            self.consultantleft_important = 0
    
class HelpdeskTicketType(models.Model):
    _inherit = 'helpdesk.ticket'
    
    types_ids = fields.Many2one('ticket.type.types', 'النوع الفرعي', domain="[('ticket_type_id', '=', ticket_type_id)]")
    
    def _default_access_token(self):
        return str(uuid.uuid4())

    access_token = fields.Char('Security Token', required=True, default=_default_access_token, readonly=True)

    response = fields.Text(string='الرد على استشارة العميل')
    service_standard = fields.Selection([
        ('عادي', 'عادي'),
        ('مستعجل', 'مستعجل'),
        ('طارئ', 'طارئ')], string='معيار الخدمة', required=True, default='عادي')
    
    today = fields.Date(default=datetime.today().date())
    month = fields.Date(compute='_count_month')
    
    def _count_month(self):
        for ticket in self:
                month = ticket.today - timedelta(days = 30)
                ticket.month = month
                
    service_count = fields.Integer(compute='_service_count')
    
    def _service_count(self):
        if self.service_standard and self.partner_id:
            if self.partner_id.parent_id:
                        services_standard = self.env['helpdesk.ticket'].search([('partner_id.parent_id','=',self.partner_id.parent_id.id),
                                                                   ('service_standard', '=', self.service_standard),
                                                                   ('ticket_type_id.name', '=', self.ticket_type_id.name),
                                                                   ('create_date', '<=', self.today),
                                                                   ('create_date', '>=', self.month)])


            else:
                        services_standard = self.env['helpdesk.ticket'].search([('partner_id', '=', self.partner_id.id),
                                                                   ('service_standard', '=', self.service_standard),
                                                                   ('ticket_type_id.name', '=', self.ticket_type_id.name),
                                                                   ('create_date', '<=', self.today),
                                                                   ('create_date', '>=', self.month)])

            service_standard = str(len(services_standard))
            self.service_count = service_standard
        else:
            self.service_count = 0
                
    @api.constrains('service_standard')
    def _check_service_standards(self):
        for ticket in self:
            if ticket.service_standard and ticket.partner_id and ticket.service_standard and ticket.ticket_type_id:
                for ticket_type in ticket.ticket_type_id:                
                    if ticket.service_standard == 'عادي':
                        if ticket_type.normal_tickets != 0:
                            if ticket.service_count > ticket_type.normal_tickets:
                                raise ValidationError(_('لقد تجاوزت عدد الطلبات العادية في الشهر'))    
                    if ticket.service_standard == 'مستعجل':
                        if ticket_type.urgent_tickets != 0:
                            if ticket.service_count > ticket_type.urgent_tickets:
                                raise ValidationError(_('لقد تجاوزت عدد الطلبات المستعجلة في الشهر'))    
                    if ticket.service_standard == 'طارئ':
                        if ticket_type.very_urgent_tickets != 0:
                            if ticket.service_count > ticket_type.very_urgent_tickets:
                                raise ValidationError(_('لقد تجاوزت عدد الطلبات الطارئة في الشهر'))    
    
    service_days = fields.Char("الوقت المتبقي لتقديم الخدمة", compute='_count_service_days', help="عدد الأيام المتوقعة لتقديم الخدمة", store=True)
    service_days_left = fields.Char("الأيام المتبقية لتقديم الخدمة", compute='_count_days', help="عدد الأيام المتوقعة لتقديم الخدمة")
    service_date = fields.Date("الوقت المتوقع لتقديم الخدمة", compute='_count_service', store=True, tracking=True)
 
    @api.depends('service_days_left')
    def _count_service_days(self):
        for ticket in self:
            if ticket.service_days_left:
                service_days_left = ticket.service_days_left
                if ticket.service_days_left.isnumeric():
                    if int(ticket.service_days_left) <= 0:
                        service_days_left = 'سيتم تقديمها في أقرب وقت'
            ticket.service_days = service_days_left
                
    @api.depends('service_date','service_standard','stage_id.sequence','ticket_type_id.name','stage_id.clf_number','stage_id')
    def _count_days(self):
        for ticket in self:
            service_days_left = False
            date_start = 0
            if ticket.stage_id.sequence == 2 or ticket.stage_id.clf_number == 5:
                service_days_left = 'تم تقديم الخدمة'
            elif ticket.stage_id.sequence == 3:
                service_days_left = 'تم إلغاء الخدمة'
            elif ticket.ticket_type_id.name == 'قضية':
                service_days_left = 'سيتم تقديمها في أقرب وقت'
            else:
                if ticket.service_date:
                    date_start = fields.Date.from_string(ticket.service_date)
                    service_days = (date_start - datetime.today().date()).days
                    service_days_left = str(service_days)
                else:
                    service_days_left = 'لم يتم التحديد'
            ticket.service_days_left = service_days_left
                        
    @api.depends('service_standard','ticket_type_id.name')
    def _count_service(self):
        for ticket in self:
            if ticket.create_date and ticket.service_standard and ticket.ticket_type_id:
                a = 0
                if ticket.service_standard == 'عادي':
                    a = ticket.ticket_type_id.normal_time_taken
                    
                elif ticket.service_standard == 'مستعجل':
                    a = ticket.ticket_type_id.urgent_time_taken

                elif ticket.service_standard == 'طارئ':
                    a = ticket.ticket_type_id.very_urgent_time_taken

                new_due_date = ticket.create_date + timedelta(days = a)
                ticket.service_date = new_due_date
            else:
                ticket.service_date = False
                
    litigation_number = fields.Integer(compute='_compute_litigation_number')
    
    def _compute_litigation_number(self):
        litigation_number = self.env['litigation.litigation'].search_count([('ticket_id', 'in', self.ids)])
        for record in self:
            record.litigation_number = litigation_number
            
    def action_get_litigation_tree_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('litigation.view_litigation')
        action['domain'] = str([('ticket_id', '=', self.ids)])
        return action

    consulting_number = fields.Integer(compute='_compute_consulting_number')
    
    def _compute_consulting_number(self):
        consulting_number = self.env['consulting.consulting'].search_count([('ticket_id', 'in', self.ids)])
        for record in self:
            record.consulting_number = consulting_number
            
    def action_get_consulting_tree_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('litigation.view_consulting')
        action['domain'] = str([('ticket_id', '=', self.ids)])
        return action
    
    contractconsulting_number = fields.Integer(compute='_compute_contractconsulting_number')
    
    def _compute_contractconsulting_number(self):
        contractconsulting_number = self.env['contractconsulting.contractconsulting'].search_count([('ticket_id', 'in', self.ids)])
        for record in self:
            record.contractconsulting_number = contractconsulting_number
            
    def action_get_contractconsulting_tree_view(self):
        action = self.env['ir.actions.act_window']._for_xml_id('litigation.view_contractconsulting')
        action['domain'] = str([('ticket_id', '=', self.ids)])
        return action
    
    
    litigation_url = fields.Char(compute='_get_urls')
    consulting_url = fields.Char(compute='_get_urls')
    contractconsulting_url = fields.Char(compute='_get_urls')

    def _get_urls(self):
        for ticket in self:
            litigation_url = False
            consulting_url = False
            contractconsulting_url = False
            litigation = self.env['litigation.litigation'].search([('ticket_id', 'in', self.ids)], limit=1)
            consulting = self.env['consulting.consulting'].search([('ticket_id', 'in', self.ids)], limit=1)
            contractconsulting = self.env['contractconsulting.contractconsulting'].search([('ticket_id', 'in', self.ids)], limit=1)
            if litigation:
                litigation_url = litigation.portal_url
            if consulting:
                consulting_url = consulting.portal_url
            if contractconsulting:
                contractconsulting_url = contractconsulting.portal_url
            ticket.litigation_url = litigation_url
            ticket.consulting_url = consulting_url
            ticket.contractconsulting_url = contractconsulting_url