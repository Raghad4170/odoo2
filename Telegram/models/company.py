# -*- coding: utf-8 -*-

from odoo import models, api, _, fields

class users(models.Model):
    _inherit = 'res.users'

    chat_id = fields.Char(string='معرف محادثة التليقرام')

class partners(models.Model):
    _inherit = 'res.partner'

    chat_id = fields.Char(string='معرف محادثة التليقرام')

    
#     chat_id = fields.Char(string='معرف محادثة التليقرام', compute='_get_chat_id', readonly=False, store=True)

    
#     @api.depends('user_ids','user_ids.chat_id')
#     def _get_chat_id(self):
#         for partner in self:
#             if partner.user_ids:
#                 if partner.user_ids.chat_id:
#                     partner.chat_id = partner.user_ids.chat_id
                

class ResCompany(models.Model):
    _inherit = "res.company"
    
    bank_telegram = fields.Char(string="التقرير المالي بالتليجرام")   
    session_telegram = fields.Char(string="تقرير تسجيل الدخول بالتليجرام")
    attendance_telegram = fields.Char(string="تقرير الحضور بالتليجرام")
    ticket_telegram = fields.Char(string="تقرير الخدمات القانونية بالتليجرام")
    telegram_token = fields.Char(string="توكين تليجرام")
    
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bank_telegram = fields.Char(related='company_id.bank_telegram', readonly=False)
    session_telegram = fields.Char(related='company_id.session_telegram', readonly=False)
    attendance_telegram = fields.Char(related='company_id.attendance_telegram', readonly=False)
    ticket_telegram = fields.Char(related='company_id.ticket_telegram', readonly=False)
    telegram_token = fields.Char(related='company_id.telegram_token', readonly=False)