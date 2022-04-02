# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime

class correcting(models.Model):
    _name = 'attendance.correcting'
    _description = 'تصحيح حضور'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = 'date desc'

    name = fields.Selection([
            ('تصحيح تسجيل خروج', 'تصحيح تسجيل خروج'),
            ('تصحيح تسجيل دخول', 'تصحيح تسجيل دخول'),
            ], string='نوع الدعوى', default='تصحيح تسجيل دخول', required=True, tracking=True)
    company_id = fields.Many2one(related='create_uid.company_id')
    date = fields.Date(string='اليوم المراد تصحيحه', tracking=True, required=True)
    true_date = fields.Datetime(string='الوقت الصحيح', required=True)
    message = fields.Text(string="السبب")
    file = fields.Binary(string='المرفقات')
    state = fields.Selection([
            ('طلب جديد', 'طلب جديد'),
            ('معلق', 'معلق'),
            ('معتمد', 'معتمد'),
            ], string='الحالة', default='طلب جديد', required=True, tracking=True)

    def action_approve(self):
        self.write({'state': 'معتمد'})
        return True

    def action_suspend(self):
        self.write({'state': 'معلق'})
        return True

    def action_draft(self):
        self.write({'state': 'طلب جديد'})
        return True




