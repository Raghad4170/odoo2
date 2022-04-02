# -*- coding: utf-8 -*-

from odoo import models, fields, api

class error404(models.Model):
    _name = 'error404.error404'
    _description = 'error404.error404'

    name = fields.Char(string='المشكلة')
    user_id = fields.Many2one('res.users', string='المسؤول', groups="error404.error404_user")
    description = fields.Text(string='وصف المشكلة')
    note = fields.Text(string='ملاحظات من التقنية')
    file = fields.Binary('المرفقات')    
    state = fields.Selection([
        ('sent','تم إرسالها'),
        ('review','يتم مراجعتها من قبل القسم التقني'),
        ('solved', 'تم حلها'),
        ('canceled', 'ملغية')], required=True, default='sent', string='الحالة')
    is_error404 = fields.Boolean(compute="_check_is_error404")
    
    def _check_is_error404(self):
        for error404 in self:
            if self.env.user.has_group('error404.error404_user'):
                error404.is_error404 = True
            else:
                error404.is_error404 = False

    def action_assign(self):
        for error404 in self:
            error404.user_id = self.env.user
            error404.write({'state':'review'})
       
    def action_solve(self):
        self.sudo().write({'state':'solved'})
        
    def action_cancel(self):
        self.sudo().write({'state':'canceled'})