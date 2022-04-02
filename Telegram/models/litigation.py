# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.http import request
from odoo import http
from urllib.parse import quote_plus
import requests
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning
from datetime import datetime, timedelta, date

class litigationtelegram(models.Model):
    _inherit = 'litigation.litigation'
            
    def action_approve(self):
        for litigation in self:
            if litigation.company_id.telegram_token and litigation.company_id.ticket_telegram:
                if litigation.opponent and litigation.partner_id:
                    message = 'تمت الموافقة من قبل  ' + litigation.env.user.name + ' على قضية ' + litigation.name + ' الخاصة بالعميل ' + litigation.partner_id.name + ' ضد ' + litigation.opponent.name
                    url = ("%3Ca+href%3D%27{}".format(quote_plus(litigation.url)))
                    chat_id = litigation.company_id.ticket_telegram
                    token = litigation.company_id.telegram_token
                    send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                    send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                    response = requests.post(send_text)
                else:
                    raise UserError(('الرجاء إدخال معلومات الخصم والعميل قبل الموافقة'))
        return super(litigationtelegram, self).action_approve()
        
        
    def action_confirm(self):
        for litigation in self:
            if litigation.company_id.telegram_token:
                if litigation.lawyer_manager.chat_id:
                    if litigation.opponent and litigation.partner_id:
                        message = 'تم تقديم طلب الاعتماد من قبل المحامي ' + litigation.env.user.name + ' على قضية ' + litigation.name + ' الخاصة بالعميل ' + litigation.partner_id.name + ' ضد ' + litigation.opponent.name + ' نأمل منكم الإطلاع والتعميد.'
                        url = ("%3Ca+href%3D%27{}".format(quote_plus(litigation.url)))
                        chat_id = litigation.lawyer_manager.chat_id
                        token = litigation.company_id.telegram_token
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                        response = requests.post(send_text)
                    else:
                        raise UserError(('الرجاء إدخال معلومات الخصم والعميل قبل الإعتماد'))
        return super(litigationtelegram, self).action_confirm()

            
    def action_refuse(self):
        for litigation in self:
            if litigation.company_id.telegram_token:
                for helper in litigation.helper_ids:
                    if helper.chat_id:
                        if litigation.partner_id:
                            message = 'تمت إعادة قضية ' + litigation.name + ' الخاصة بالعميل ' + litigation.partner_id.name + ' من قبل ' + litigation.env.user.name + ' نأمل منكم مراجعتها وإعادة تقديم طلب الإعتماد'
                            url = ("%3Ca+href%3D%27{}".format(quote_plus(litigation.url)))
                            chat_id = helper.chat_id
                            token = litigation.company_id.telegram_token
                            send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                            send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                            response = requests.post(send_text)
                        else:
                            raise UserError(('الرجاء إدخال معلومات العميل قبل الرفض'))
        return super(litigationtelegram, self).action_refuse()


    @api.model_create_multi
    def create(self, vals_list):
        record = super(litigationtelegram, self).create(vals_list)
        if record.company_id.telegram_token:
            message = 'تم تعيينك على قضية ' + record.name + ' الخاصة بالعميل ' + record.partner_id.name + ' نأمل منكم مراجعتها والبدأ بها في أقرب وقت '
            url = ("%3Ca+href%3D%27{}".format(quote_plus(record.url)))
            token = record.company_id.telegram_token

            if record.user_id != self.env.user:
                if record.user_id.chat_id:
                    chat_id = record.user_id.chat_id
                    send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                    send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                    response = requests.post(send_text)

            for helper in record.helper_ids:
                if helper != self.env.user:
                    if helper.chat_id:
                        chat_id = helper.chat_id
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                        response = requests.post(send_text)
        return record
            

class reporttelegram(models.Model):
    _inherit = 'litigation.report'
    
    
    message = fields.Text(compute='get_message')
    
    def get_message(self):
        for report in self:
            report.message = '\n' + 'ضبط الجلسة:' + '\n' + report.summary
        
    def action_confirm(self):
        for report in self:
            if report.company_id.telegram_token:
                if report.lawyer_manager.chat_id:
                    if report.litigation_id and report.partner_id:
                        message = 'تم تقديم طلب الاعتماد من قبل المحامي ' + report.env.user.name + ' على ' + report.name + ' التابعة لقضية ' + report.litigation_id.name + ' الخاصة بالعميل ' + report.partner_id.name + ' نأمل منكم الإطلاع والتعميد.'
                        url = ("%3Ca+href%3D%27{}".format(quote_plus(report.url)))
                        chat_id = report.lawyer_manager.chat_id
                        token = report.company_id.telegram_token
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E' + ("{}".format(quote_plus(report.message))) 
                        response = requests.post(send_text)
                    else:
                        raise UserError(('الرجاء إدخال معلومات القضية والعميل قبل الإعتماد'))
        return super(reporttelegram, self).action_confirm()
                
        
    def action_refuse(self):
        for report in self:
            if report.company_id.telegram_token:
                for helper in report.helper_ids:
                    if helper.chat_id:
                        if report.partner_id:
                            message = 'تمت إعادة  ' + report.name + ' التابعة لقضية ' + report.litigation_id.name + ' الخاصة بالعميل ' + report.partner_id.name + ' من قبل ' + report.env.user.name + ' نأمل منكم مراجعتها وإعادة تقديم طلب الإعتماد'
                            url = ("%3Ca+href%3D%27{}".format(quote_plus(report.url)))
                            chat_id = helper.chat_id
                            token = report.company_id.telegram_token
                            send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                            send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                            response = requests.post(send_text)
                        else:
                            raise UserError(('الرجاء إدخال معلومات العميل قبل الرفض'))
        return super(reporttelegram, self).action_refuse()

        
        
    def action_approve(self):
        for report in self:
            if report.company_id.telegram_token:
                token = report.company_id.telegram_token
                if report.litigation_id and report.partner_id and report.litigation_id.opponent and report.litigation_id.lawsuit:
                    url = ("%3Ca+href%3D%27{}".format(quote_plus(report.portal_url)))
                    here = 'هنا'
                    portal_url = url + '%27%3E' + here + '%3C%2Fa%3E'

                    if report.partner_id.user_ids.chat_id:
                        portal_message = ('شريكنا العزيز ' + report.partner_id.name + ' نحيطكم علما بأنه تم إضافة تحديث لقضيتكم المقامة ضد ' 
                                        + report.litigation_id.opponent.name + ' بشأن ' + report.litigation_id.lawsuit + ' ومفاده:' + '\n' 
                                        + report.summary + '\n' + ' وللمزيد يمكنكم الاطلاع عليها من خلال الرابط التالي:' + '\n')
                        chat_id = report.partner_id.user_ids.chat_id
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + ("{}".format(quote_plus(portal_message))) + portal_url
                        response = requests.post(send_text)
                        
                        
                    if report.partner_id.full_permission:
                        for full_permission in report.partner_id.full_permission:
                            if full_permission.user_ids.chat_id:
                                portal_message = ('شريكنا العزيز ' + full_permission.name + ' نحيطكم علما بأنه تم إضافة تحديث لقضيتكم المقامة ضد ' 
                                                + report.litigation_id.opponent.name + ' بشأن ' + report.litigation_id.lawsuit + ' ومفاده:' + '\n' 
                                                + report.summary + '\n' + ' وللمزيد يمكنكم الاطلاع عليها من خلال الرابط التالي:' + '\n')
                                chat_id = full_permission.user_ids.chat_id
                                send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                                send_text = send + ("{}".format(quote_plus(portal_message))) + portal_url
                                response = requests.post(send_text)
                                
                if report.company_id.ticket_telegram:
                    message = 'تمت الموافقة من قبل  ' + report.env.user.name + ' على ' + report.name + ' التابعة لقضية ' + report.litigation_id.name  + ' الخاصة بالعميل ' + report.partner_id.name
                    url = ("%3Ca+href%3D%27{}".format(quote_plus(report.url)))
                    chat_id = report.company_id.ticket_telegram
                    send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                    send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                    response = requests.post(send_text)
                else:    
                    raise UserError(('الرجاء إدخال معلومات القضية والعميل قبل الموافقة'))
        return super(reporttelegram, self).action_approve()                
                
class AttorneyTelegram(models.Model):
    _inherit = 'attorney.attorney'
    

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
                        message = ("تبقى على إنتهاء وكالة " + attorney.partner_id.name + " شهر واحد")
                    elif days_15 == today:
                        message = ("تبقى على إنتهاء وكالة " + attorney.partner_id.name + " 15 يوم")
                    elif days_10 == today:
                        message = ("تبقى على إنتهاء وكالة " + attorney.partner_id.name + " 10 أيام")
                    elif days_3 == today:
                        message = ("تبقى على إنتهاء وكالة " + attorney.partner_id.name + " 3 أيام")
                    elif day_1 == today:
                        message = ("تبقى على إنتهاء وكالة " + attorney.partner_id.name + " يوم واحد")
                    if attorney.user_id.chat_id:
                        url = ("%3Ca+href%3D%27{}".format(quote_plus(attorney.url)))
                        chat_id = attorney.user_id.chat_id
                        token = attorney.company_id.telegram_token
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                        response = requests.post(send_text)
                    if attorney.user_id.lawyer_manager.chat_id:
                        url = ("%3Ca+href%3D%27{}".format(quote_plus(attorney.url)))
                        chat_id = attorney.user_id.lawyer_manager.chat_id
                        token = attorney.company_id.telegram_token
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                        response = requests.post(send_text)
                    if attorney.company_id.ticket_telegram:
                        url = ("%3Ca+href%3D%27{}".format(quote_plus(attorney.url)))
                        chat_id = attorney.company_id.ticket_telegram
                        token = attorney.company_id.telegram_token
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                        response = requests.post(send_text)
            return super(AttorneyTelegram, self)._ending_date_reminder()                


class consultingtelegram(models.Model):
    _inherit = 'consulting.consulting'
    
    
    message = fields.Text(compute='get_message')
    
    def get_message(self):
        for consulting in self:
            consulting.message = '\n' + 'ملخص استشارة العميل:' + '\n' + consulting.summary + '\n' + '\n' + 'الرأي الاستشاري المقترح:' + '\n' + consulting.consult
                
    def action_confirm(self):
        for consulting in self:
            if consulting.company_id.telegram_token:
                if consulting.lawyer_manager.chat_id:
                    if consulting.partner_id and consulting.summary and consulting.consult:
                        message = 'تم تقديم طلب الاعتماد من قبل المستشار ' + consulting.env.user.name + ' على استشارة ' + consulting.name + ' الخاصة بالعميل ' + consulting.partner_id.name + ' نأمل منكم الإطلاع والتعميد.'
                        
                        quote_message = ("{}".format(quote_plus(message)))
                        quote_consulting_message = ("{}".format(quote_plus(consulting.message)))
                        quote_consult = ("{}".format(quote_plus(consulting.consult)))
                        quote_summary = ("{}".format(quote_plus(consulting.summary)))

                        url = ("%3Ca+href%3D%27{}".format(quote_plus(consulting.url)))
                        chat_id = consulting.lawyer_manager.chat_id
                        token = consulting.company_id.telegram_token
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + url + '%27%3E' + quote_message + '%3C%2Fa%3E' +  quote_consulting_message
                        if len(send_text) > 20000:
                            first = send + url + '%27%3E' + message + '%3C%2Fa%3E' + '\n' + 'ملخص استشارة العميل:' + '\n' + quote_summary
                            second = send + 'تابع: ' + '\n' + 'الرأي الاستشاري المقترح:' + '\n' + quote_summary
                            if len(first) > 20000:
                                first = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                                second = send + 'تابع: ' + '\n' + 'ملخص استشارة العميل:' + '\n' + quote_summary
                                third = send + 'تابع: ' + '\n' + 'الرأي الاستشاري المقترح:' + '\n' + quote_summary
                                response = requests.post(first) and requests.post(second) and requests.post(third)
                            else:
                                response = requests.post(first) and requests.post(second)
                        else:
                            response = requests.post(send_text)
                    else:
                        raise UserError(('الرجاء إدخال معلومات العميل والاستشارة قبل الإعتماد'))
        return super(consultingtelegram, self).action_confirm()
        
                
    def action_approve(self):
        for consulting in self:
            if consulting.company_id.telegram_token:
                token = consulting.company_id.telegram_token

                if consulting.partner_id and consulting.summary and consulting.consult:
                    quote_summary = ("{}".format(quote_plus(consulting.summary)))
                    quote_consult = ("{}".format(quote_plus(consulting.consult)))
                    
                    url = ("%3Ca+href%3D%27{}".format(quote_plus(consulting.portal_url)))
                    here = 'هنا'
                    portal_url = url + '%27%3E' + here + '%3C%2Fa%3E'
                    
                    if consulting.partner_id.user_ids.chat_id:
                        partner_message = ('شريكنا العزيز ' + consulting.partner_id.name + ' نحيطكم علما بأنه تم الإجابة على استشارتكم في البوابة الإلكترونية. ومفادها: ' + '\n' 
                                    + 'طلب الاستشارة بخصوص:' + '\n' + quote_summary + '\n' + '\n' + 'والتوصية المقدمة:' + '\n' + quote_consult 
                                    + '\n' + 'وللمزيد يمكنكم الاطلاع عليها من خلال الرابط التالي: ' + '\n')
                        chat_id = consulting.partner_id.user_ids.chat_id
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + partner_message + portal_url

                        if len(send_text) > 20000:
                            message_1 = ('شريكنا العزيز ' + consulting.partner_id.name + ' نحيطكم علما بأنه تم الإجابة على استشارتكم في البوابة الإلكترونية. ومفادها: ' + '\n' 
                                            + 'طلب الاستشارة بخصوص:' + '\n' + quote_summary + '\n' + 'يتبع..')
                            message_2 = ('تابع:' + '\n' + 'والتوصية المقدمة:' + '\n' + quote_consult 
                                            + '\n' + 'وللمزيد يمكنكم الاطلاع عليها من خلال الرابط التالي: ' + '\n')
                            first = send + message_1
                            second = send + message_2 + portal_url
                            response = requests.post(first) and requests.post(second)
                        else:
                            response = requests.post(send_text)

                        
                    for full_permission in consulting.partner_id.full_permission:
                        if full_permission.user_ids.chat_id:
                            partner_message = ('شريكنا العزيز ' + full_permission.name + ' نحيطكم علما بأنه تم الإجابة على استشارتكم في البوابة الإلكترونية. ومفادها: ' + '\n' 
                                        + 'طلب الاستشارة بخصوص:' + '\n' + quote_summary + '\n' + '\n' + 'والتوصية المقدمة:' + '\n' + quote_consult 
                                        + '\n' + ' وللمزيد يمكنكم الاطلاع عليها من خلال الرابط التالي: ' + '\n')
                            chat_id = full_permission.user_ids.chat_id
                            send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                            send_text = send + partner_message + portal_url

                            if len(send_text) > 20000:
                                message_1 = ('شريكنا العزيز ' + full_permission.name + ' نحيطكم علما بأنه تم الإجابة على استشارتكم في البوابة الإلكترونية. ومفادها: ' + '\n' 
                                                + 'طلب الاستشارة بخصوص:' + '\n' + quote_summary + '\n' + 'يتبع..')
                                message_2 = ('تابع:' + '\n' + 'والتوصية المقدمة:' + '\n' + quote_consult 
                                                + '\n' + ' وللمزيد يمكنكم الاطلاع عليها من خلال الرابط التالي: ' + '\n')
                                first = send + message_1
                                second = send + message_2 + portal_url
                                response = requests.post(first) and requests.post(second)
                            else:
                                response = requests.post(send_text)
                                
                    if consulting.company_id.ticket_telegram:
                        message = 'تمت الموافقة من قبل ' + consulting.env.user.name + ' على استشارة ' + consulting.name + ' الخاصة بالعميل ' + consulting.partner_id.name
                        url = ("%3Ca+href%3D%27{}".format(quote_plus(consulting.url)))
                        chat_id = consulting.company_id.ticket_telegram
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E' + '\n' + 'ملخص استشارة العميل:' + '\n' + quote_summary + '\n' + 'الرأي الاستشاري المقترح:' + quote_consult
                        if len(send_text) > 20000:
                            first = send + url + '%27%3E' + message + '%3C%2Fa%3E' + '\n' + 'ملخص استشارة العميل:' + '\n' + quote_summary
                            second = send + 'تابع: ' + '\n' + 'الرأي الاستشاري المقترح:' + '\n' + ("{}".format(quote_plus(consulting.consult)))
                            if len(first) > 20000:
                                first = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                                second = send + 'تابع: ' + '\n' + 'ملخص استشارة العميل:' + '\n' + quote_summary
                                third = send + 'تابع: ' + '\n' + 'الرأي الاستشاري المقترح:' + '\n' + quote_consult
                                response = requests.post(first) and requests.post(second) and requests.post(third)
                            else:
                                response = requests.post(first) and requests.post(second)
                        else:
                            response = requests.post(send_text)
                else:   
                    raise UserError(('الرجاء إدخال معلومات العميل والاستشارة قبل الموافقة'))

        return super(consultingtelegram, self).action_approve()
        
        
        
        
    def action_refuse(self):
        for consulting in self:
            if consulting.company_id.telegram_token:
                for helper in consulting.helper_ids:
                    if helper.chat_id:
                        if consulting.partner_id:
                            message = 'تمت إعادة استشارة ' + consulting.name + ' الخاصة بالعميل ' + consulting.partner_id.name + ' من قبل ' + consulting.env.user.name + ' نأمل منكم مراجعتها وإعادة تقديم طلب الإعتماد'
                            url = ("%3Ca+href%3D%27{}".format(quote_plus(consulting.url)))
                            chat_id = helper.chat_id
                            token = consulting.company_id.telegram_token
                            send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                            send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                            response = requests.post(send_text)
                        else:
                            raise UserError(('الرجاء إدخال معلومات الخصم والعميل قبل الموافقة'))
        return super(consultingtelegram, self).action_refuse()

            
    @api.model_create_multi
    def create(self, vals_list):
        record = super(consultingtelegram, self).create(vals_list)
        if record.company_id.telegram_token:
            token = record.company_id.telegram_token
            message = 'تم تعيينك على استشارة ' + record.name + ' الخاصة بالعميل ' + record.partner_id.name + '  نأمل منكم مراجعتها والانتهاء منها في موعد أقصاه ' + str(record.service_date)
            url = ("%3Ca+href%3D%27{}".format(quote_plus(record.url)))

            if record.user_id != self.env.user:
                if record.user_id.chat_id:
                    chat_id = record.user_id.chat_id
                    send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                    send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                    response = requests.post(send_text)

            for helper in record.helper_ids:
                if helper != self.env.user:
                    if helper.chat_id:
                        chat_id = helper.chat_id
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                        response = requests.post(send_text)
        return record

        
class contractconsultingtelegram(models.Model):
    _inherit = 'contractconsulting.contractconsulting'
    
    def action_confirm(self):
        for contract in self:
            if contract.company_id.telegram_token:
                if contract.lawyer_manager.chat_id:
                    if contract.partner_id:
                        draft_contract = ''
                        recommended_contract = ''
                        sign_contract = ''
                        if contract.draft_contract:
                            draft_url = ("%3Ca+href%3D%27{}".format(quote_plus(contract.draft_contract)))
                            draft_contract = '\n' + draft_url+ '%27%3Eمسودة العقد الأولية%3C%2Fa%3E'
                        if contract.recommended_contract:
                            recommended_url = ("%3Ca+href%3D%27{}".format(quote_plus(contract.recommended_contract)))
                            recommended_contract = '\n' + recommended_url+ '%27%3Eالعقد الموصى به%3C%2Fa%3E'
                        if contract.sign_contract:
                            sign_url = ("%3Ca+href%3D%27{}".format(quote_plus(contract.sign_contract)))
                            sign_contract = '\n' + sign_url + '%27%3Eالعقد الموقع مع العميل%3C%2Fa%3E'
                        
                        message = 'تم تقديم طلب الاعتماد من قبل المستشار ' + contract.env.user.name + ' على استشارة العقد ' + contract.name + ' الخاصة بالعميل ' + contract.partner_id.name + ' نأمل منكم الإطلاع والتعميد.'
                        url = ("%3Ca+href%3D%27{}".format(quote_plus(contract.url)))
                        chat_id = contract.lawyer_manager.chat_id
                        token = contract.company_id.telegram_token
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E' + draft_contract + recommended_contract + sign_contract
                        response = requests.post(send_text)
                    else:
                        raise UserError(('الرجاء إدخال معلومات العميل قبل الإعتماد'))
        return super(contractconsultingtelegram, self).action_confirm()
    
    def action_approve(self):
        for contract in self:
            if contract.company_id.telegram_token:
                token = contract.company_id.telegram_token
                draft_contract = ''
                recommended_contract = ''
                sign_contract = ''
                
                if contract.draft_contract:
                    draft_url = ("%3Ca+href%3D%27{}".format(quote_plus(contract.draft_contract)))
                    draft_contract = '\n' + draft_url+ '%27%3Eمسودة العقد الأولية%3C%2Fa%3E'
                if contract.recommended_contract:
                    recommended_url = ("%3Ca+href%3D%27{}".format(quote_plus(contract.recommended_contract)))
                    recommended_contract = '\n' + recommended_url+ '%27%3Eالعقد الموصى به%3C%2Fa%3E'
                if contract.sign_contract:
                    sign_url = ("%3Ca+href%3D%27{}".format(quote_plus(contract.sign_contract)))
                    sign_contract = '\n' + sign_url + '%27%3Eالعقد الموقع مع العميل%3C%2Fa%3E'
                            
                url = ("%3Ca+href%3D%27{}".format(quote_plus(contract.portal_url)))
                here = 'هنا'
                portal_url = url + '%27%3E' + here + '%3C%2Fa%3E'

                            
                if contract.partner_id.user_ids.chat_id:
                    portal_message = ('شريكنا العزيز ' + contract.partner_id.name + ' نحيطكم علما بأنه تم الإجابة على استشارتكم بخصوص ' + contract.name + ' في البوابة الإلكترونية والعقد المقترح لكم: ' 
                               + draft_contract + recommended_contract + sign_contract + '\n' + 'وللمزيد يمكنكم الإطلاع عليها من خلال الرابط التالي:' + '\n' + portal_url) 
                    chat_id = contract.partner_id.user_ids.chat_id
                    send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                    send_text = send + portal_message
                    response = requests.post(send_text)
    
                if contract.partner_id.full_permission:
                    for full_permission in contract.partner_id.full_permission:
                        if full_permission.user_ids.chat_id:
                            portal_message = ('شريكنا العزيز ' + full_permission.name + ' نحيطكم علما بأنه تم الإجابة على استشارتكم بخصوص ' + contract.name + ' في البوابة الإلكترونية والعقد المقترح لكم: ' 
                                       + draft_contract + recommended_contract + sign_contract + '\n' + 'وللمزيد يمكنكم الإطلاع عليها من خلال الرابط التالي:' + '\n' + portal_url) 
                            chat_id = full_permission.user_ids.chat_id
                            send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                            send_text = send + portal_message
                            response = requests.post(send_text)   
                             
                if contract.company_id.ticket_telegram:
                    message = 'تمت الموافقة من قبل ' + contract.env.user.name + ' على استشارة ' + contract.name + ' الخاصة بالعميل ' + contract.partner_id.name
                    url = ("%3Ca+href%3D%27{}".format(quote_plus(contract.url)))
                    chat_id = contract.company_id.ticket_telegram
                    send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                    send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E' + draft_contract + recommended_contract + sign_contract

        return super(contractconsultingtelegram, self).action_approve()


    def action_refuse(self):
        for contract in self:
            if contract.company_id.telegram_token:
                for helper in contract.helper_ids:
                    if helper.chat_id:
                        if contract.partner_id:
                            message = 'تمت إعادة استشارة العقد ' + contract.name + ' الخاصة بالعميل ' + contract.partner_id.name + ' من قبل ' + contract.env.user.name + ' نأمل منكم مراجعتها وإعادة تقديم طلب الإعتماد'
                            url = ("%3Ca+href%3D%27{}".format(quote_plus(contract.url)))
                            chat_id = helper.chat_id
                            token = contract.company_id.telegram_token
                            send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                            send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                            response = requests.post(send_text)
                        else:
                            raise UserError(('الرجاء إدخال معلومات الخصم والعميل قبل الموافقة'))
        return super(contractconsultingtelegram, self).action_refuse()

            
    @api.model_create_multi
    def create(self, vals_list):
        record = super(contractconsultingtelegram, self).create(vals_list)
        if record.company_id.telegram_token:
            token = record.company_id.telegram_token
            message = 'تم تعيينك على استشارة العقد ' + record.name + ' الخاصة بالعميل ' + record.partner_id.name + ' نأمل منكم مراجعتها والانتهاء منها في موعد أقصاه ' + str(record.service_date)
            url = ("%3Ca+href%3D%27{}".format(quote_plus(record.url)))
            
            if record.user_id != self.env.user:
                if record.user_id.chat_id:
                    chat_id = record.user_id.chat_id
                    send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                    send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                    response = requests.post(send_text)

            for helper in record.helper_ids:
                if helper != self.env.user:
                    if helper.chat_id:
                        chat_id = helper.chat_id
                        send = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=HTML&text='
                        send_text = send + url + '%27%3E' + message + '%3C%2Fa%3E'
                        response = requests.post(send_text)
        return record