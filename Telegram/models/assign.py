# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.http import request
from odoo import http
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup


class balaghstelegram(models.Model):
    _inherit = 'balagh.balagh'

    url = fields.Char(compute='get_url')
    
    def get_url(self):
        for balagh in self:
            base_url = balagh.company_id.website
            balagh.url = base_url + '/web#id=' + str(balagh.id) + '&model=balagh.balagh&view_type=form'
    
    @api.model_create_multi
    def create(self, vals_list):
        record = super(balaghstelegram, self).create(vals_list)
        if record.company_id.telegram_token:
            if record.user_id != self.env.user:
                if record.user_id.chat_id:
                    message = 'تم تعيينك على  ' + record.name + ' التابع للعميل ' + record.partner_id.name + ' نأمل منكم مراجعته وتقديم البلاغ في أقرب وقت ممكن '
                    quote_message = ("{}".format(quote_plus(message)))
                    url = ("%3Ca+href%3D%27{}".format(quote_plus(record.url)))
                    token = record.company_id.telegram_token
                    chat_id = record.user_id.chat_id
                    send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                    send_text = send + url + '%27%3E' + quote_message + '%3C%2Fa%3E'
                    response = requests.post(send_text)
        return record
    
    
class slatetelegram(models.Model):
    _inherit = 'internal.slate'
    
    url = fields.Char(compute='get_url')
    
    def get_url(self):
        base_url = self.company_id.website
        self.url = base_url + '/web#id=' + str(self.id) + '&model=internal.slate&view_type=form'

    @api.model_create_multi
    def create(self, vals_list):
        record = super(slatetelegram, self).create(vals_list)
        if record.company_id.telegram_token:
            if record.user_id != self.env.user:
                if record.user_id.chat_id:
                    message = 'تم تعيينك على  ' + record.name + ' نأمل منكم مراجعتها والتنسيق مع العميل والمحامي المناسب لإكمال اللائحة '
                    quote_message = ("{}".format(quote_plus(message)))
                    url = ("%3Ca+href%3D%27{}".format(quote_plus(record.url)))
                    token = record.company_id.telegram_token
                    chat_id = record.user_id.chat_id
                    send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                    send_text = send + url + '%27%3E' + quote_message + '%3C%2Fa%3E'
                    response = requests.post(send_text)
        return record
    
    
class MailThreadtelegram(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_thread(self, message, msg_vals=False, notify_by_email=True, **kwargs):
        msg_vals = msg_vals if msg_vals else {}
        rdata = self._notify_compute_recipients(message, msg_vals)
        if not rdata:
            return rdata

        self._notify_record_by_inbox(message, rdata, msg_vals=msg_vals, **kwargs)
        if notify_by_email:
            self._notify_record_by_email(message, rdata, msg_vals=msg_vals, **kwargs)
                    
        user = self.env.user.name
        company = self.env.company
        body = msg_vals.get('body') if msg_vals else message.body
        record_name = msg_vals.get('record_name') if msg_vals else message.record_name
        res_id = msg_vals.get('res_id') if msg_vals else message.res_id
        internal = message.subtype_id.internal
        partner_ids = self.message_partner_ids
        soup = BeautifulSoup(body)
        text_body = soup.get_text()
        link = self._notify_get_action_link('view')

        if body != '':
            if not internal:
                for partner in partner_ids:
                    if partner.user_ids != self.env.user:
                        if partner.user_ids.chat_id:
                            tele_message = 'تمت إضافة رد من قبل: ' + user + '\n' + 'في سجل: ' + record_name + '\n' + ' مفاده:' + '\n' + text_body
                            quote_message = ("{}".format(quote_plus(tele_message)))
                            if partner.user_ids.has_group('base.group_user'):
                                url = ("%3Ca+href%3D%27{}".format(quote_plus(link)))                                
                                quote_message = url + '%27%3E' + quote_message + '%3C%2Fa%3E'
                            token = company.telegram_token
                            chat_id = partner.user_ids.chat_id
                            send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                            send_text = send + quote_message
                            response = requests.post(send_text)
        return rdata
