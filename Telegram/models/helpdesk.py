# Copyright to The City Law Firm
from odoo import models, fields, api, _
import requests
from urllib.parse import quote_plus
import uuid
from bs4 import BeautifulSoup

class TicketTelegram(models.Model):
    _inherit = 'helpdesk.ticket'
        
    def _default_access_token(self):
        return str(uuid.uuid4())

    access_token = fields.Char('Security Token', required=True, default=_default_access_token, readonly=True)

    portal_url = fields.Char(compute='get_the_portal_url')
    
    def get_the_portal_url(self):
        for ticket in self:
            base_url = ticket.company_id.website
            ticket.portal_url = base_url + '/helpdesk/ticket/' + str(ticket.id) + '?access_token={' + str(ticket.access_token) + "}"
            
    url = fields.Char(compute='get_url')
    
    def get_url(self):
        base_url = self.company_id.website
        self.url = base_url + '/web#id=' + str(self.id) + '&model=helpdesk.ticket&view_type=form'

    @api.model_create_multi
    def create(self, list_value):
        ticket = super(TicketTelegram, self).create(list_value)
        if ticket.company_id.telegram_token:
            token = ticket.company_id.telegram_token    
            partner_id = 'لا يوجد'    
            service_standard = 'لا يوجد'    
            ticket_type_id = 'لا يوجد'    
            service_date = 'لا يوجد'    
            description = 'لا يوجد'    
            name = 'لا يوجد'

    
            if ticket.partner_id:
                partner_id = ticket.partner_id.name
            if ticket.service_standard:
                service_standard = ticket.service_standard
            if ticket.ticket_type_id:
                ticket_type_id = ticket.ticket_type_id.name
            if ticket.service_date:
                service_date = str(ticket.service_date)
            if ticket.description:    
                soup = BeautifulSoup(ticket.description)
                description = soup.get_text()
            if ticket.name:
                name = ticket.name

            user_message = 'تم رفع طلب خدمة من قبل ' + partner_id + '\n' + 'الموضوع: ' + name + '\n' + 'نوع الخدمة: ' + ticket_type_id + '\n' + 'معيار الخدمة: ' + service_standard + '\n' + 'تفاصيل الطلب:' + '\n' + description + '\n' + 'الوقت المتوقع لتقديم الخدمة: ' + service_date
            quote_message = ("{}".format(quote_plus(user_message)))

            if ticket.company_id.ticket_telegram:
                chat_id = ticket.company_id.ticket_telegram
                send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                send_text = send + quote_message
                response = requests.post(send_text)
            
            if ticket.user_id != self.env.user:
                if ticket.user_id.chat_id:
                    chat_id = ticket.user_id.chat_id
                    message = 'تم تعيينك على التذكرة ' + name  + ' التابعة للعميل ' + partner_id + ' نأمل منكم مراجعتها وتحويلها إلى القسم والفريق المناسب.' 
                    quote_message = ("{}".format(quote_plus(message)))
                    url = ("%3Ca+href%3D%27{}".format(quote_plus(ticket.url)))
                    send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                    send_text = send + url + '%27%3E' + quote_message + '%3C%2Fa%3E'
                    response = requests.post(send_text)

            portal_url = ("%3Ca+href%3D%27{}".format(quote_plus(ticket.portal_url)))
            here = 'عرض التذكرة'
            quote_porta_url = portal_url + '%27%3E' + here + '%3C%2Fa%3E'
            portal_message = ('شريكنا العزيز ' + partner_id + ' نحيطكم علما بأنه تم استقبال طلبكم ' + name + '\n' + 'نوع الخدمة: ' + ticket_type_id 
                    + '\n' + 'معيار الخدمة: ' + service_standard + '\n' + 'تفاصيل الطلب:' + '\n' + description + '\n' + 'وتتم مراجعته من قبل خدمة العملاء، ولإضافة اي تعليقات اخرى يمكنكم الدخول على الرابط التالي: ')
            quote_portal_message = ("{}".format(quote_plus(portal_message))) + quote_porta_url 

            if ticket.partner_id.full_permission:
                for full_permission in ticket.partner_id.full_permission:
                    if full_permission.user_ids.chat_id:
                        chat_id = full_permission.user_ids.chat_id
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + quote_portal_message
                        response = requests.post(send_text)

            if ticket.partner_id:
                if ticket.partner_id.user_ids.chat_id:
                    chat_id = ticket.partner_id.user_ids.chat_id
                    send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                    send_text = send + quote_portal_message
                    response = requests.post(send_text)
        return ticket

class createlitigationstele(models.TransientModel):
    _inherit = 'create.litigations'

    def create_litigation(self):
        for ticket in self:
            if ticket.company_id.telegram_token:
                token = ticket.company_id.telegram_token    
                messgae = 'شريكنا العزيز ' + ticket.partner_id.name + ' نحيطكم علما بأن طلبكم ' + ticket.name + ' تم إحالته إلى قسم القضايا '
                if ticket.partner_id.full_permission:    
                    for full_permission in ticket.partner_id.full_permission:    
                        if full_permission.user_ids.chat_id:
                            chat_id = full_permission.user_ids.chat_id
                            send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                            send_text = send + messgae
                            response = requests.post(send_text)

                if ticket.partner_id:    
                    if ticket.partner_id.user_ids.chat_id:    
                        chat_id = ticket.partner_id.user_ids.chat_id    
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='    
                        send_text = send + messgae    
                        response = requests.post(send_text)

        return super(createlitigationstele, self).create_litigation()

class createconsultingstele(models.TransientModel):
    _inherit = 'create.consultings'

    def create_consulting(self):
        for ticket in self:
            if ticket.company_id.telegram_token:
                token = ticket.company_id.telegram_token    
                messgae = 'شريكنا العزيز ' + ticket.partner_id.name + ' نحيطكم علما بأن طلبكم ' + ticket.name + ' تم إحالته إلى قسم الاستشارات '
                if ticket.partner_id.full_permission:    
                    for full_permission in ticket.partner_id.full_permission:    
                        if full_permission.user_ids.chat_id:
                            chat_id = full_permission.user_ids.chat_id
                            send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                            send_text = send + messgae
                            response = requests.post(send_text)

                if ticket.partner_id:    
                    if ticket.partner_id.user_ids.chat_id:    
                        chat_id = ticket.partner_id.user_ids.chat_id    
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='    
                        send_text = send + messgae    
                        response = requests.post(send_text)

        return super(createconsultingstele, self).create_consulting()


class createcontractconsultingstele(models.TransientModel):
    _inherit = 'create.contractconsultings'

    def create_contractconsulting(self):
        for ticket in self:
            if ticket.company_id.telegram_token:
                token = ticket.company_id.telegram_token    
                messgae = 'شريكنا العزيز ' + ticket.partner_id.name + ' نحيطكم علما بأن طلبكم ' + ticket.name + ' تم إحالته إلى قسم العقود '
                if ticket.partner_id.full_permission:    
                    for full_permission in ticket.partner_id.full_permission:    
                        if full_permission.user_ids.chat_id:
                            chat_id = full_permission.user_ids.chat_id
                            send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                            send_text = send + messgae
                            response = requests.post(send_text)

                if ticket.partner_id:    
                    if ticket.partner_id.user_ids.chat_id:    
                        chat_id = ticket.partner_id.user_ids.chat_id    
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='    
                        send_text = send + messgae    
                        response = requests.post(send_text)

        return super(createcontractconsultingstele, self).create_contractconsulting()



