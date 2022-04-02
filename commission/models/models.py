# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class company(models.Model):
    _name = 'company.company'
    _description = 'company'

    name = fields.Char(string='الشركة')
    partner_id = fields.Many2one('res.partner', string='العميل', auto_join=True, required=True)
    user_id = fields.Many2one('res.users', string='المسؤول', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    commission_ids = fields.One2many('commission.commission', 'company', string='المجلدات')

    
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['commission_ids'] = [(0, 0, {
                            'name': name,
                        }) for name in [
                _('مجلس الإدارة'),
                _('لجنة المراجعة'), 
                _('لجنة المكافآت والترشيحات'), 
                _('لجنة إدارة المخاطر'), 
                _('لجنة الحوكمة')]]
        record = super(company, self).create(vals_list)
        return record
    
class commission(models.Model):
    _name = 'commission.commission'
    _description = 'commission'

    name = fields.Char(string='المجلد')
    company = fields.Many2one('company.company', string='الشركة', auto_join=True)
    user_id = fields.Many2one(related='company.user_id')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', related='company.partner_id', string='العميل', auto_join=True)
    sign_ids = fields.Many2many('sign.request', string='التواقيع')

