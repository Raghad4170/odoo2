# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
               
class personalstatus(models.Model):
    _name = 'personal.status.type'
    _description = 'personal status types'
    
    name = fields.Char(string='الدعوى', required=True)
    type = fields.Selection([
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
            ], string='التصنيف')
    
class penal(models.Model):
    _name = 'penal.type'
    _description = 'penal types'
    
    name = fields.Char(string='الدعوى', required=True)
    type = fields.Selection([
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
            ], string='التصنيف')
    
class execute(models.Model):
    _name = 'execute.type'
    _description = 'execute types'
    
    name = fields.Char(string='الدعوى', required=True)
    type = fields.Selection([
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ], string='التصنيف')
    
class general(models.Model):
    _name = 'general.type'
    _description = 'general types'
    
    name = fields.Char(string='الدعوى', required=True)
    type = fields.Selection([
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
            ], string='التصنيف')
    
class labor(models.Model):
    _name = 'labor.type'
    _description = 'labor types'
    
    name = fields.Char(string='الدعوى', required=True)
    type = fields.Selection([
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
            ], string='التصنيف')
    
class commercial(models.Model):
    _name = 'commercial.type'
    _description = 'commercial types'
    
    name = fields.Char(string='الدعوى', required=True)
    type = fields.Selection([
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
            ], string='التصنيف')

    
# manageral
    
    
class expropriation(models.Model):
    _name = 'expropriation.type'
    _description = 'expropriation types'
    
    name = fields.Char(string='الدعوى', required=True)
    type = fields.Selection([
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ], string='التصنيف')
    
class invention(models.Model):
    _name = 'invention.type'
    _description = 'invention types'
    
    name = fields.Char(string='الدعوى', required=True)
    type = fields.Selection([
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
            ('7', '7'),
            ], string='التصنيف')
    
class health(models.Model):
    _name = 'health.type'
    _description = 'health types'
    
    name = fields.Char(string='الدعوى', required=True)
    type = fields.Selection([
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ], string='التصنيف')
    
class compensation(models.Model):
    _name = 'compensation.type'
    _description = 'compensation types'
    
    name = fields.Char(string='الدعوى', required=True)
    type = fields.Selection([
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
            ('7', '7'),
            ('8', '8'),
            ('9', '9'),
            ], string='التصنيف')
    
class contracting(models.Model):
    _name = 'contracting.type'
    _description = 'contracting types'
    
    name = fields.Char(string='الدعوى', required=True)
    type = fields.Selection([
            ('1', '1'),
            ('2', '2'),
            ], string='التصنيف')
        
class discipline(models.Model):
    _name = 'discipline.type'
    _description = 'discipline types'
    
    name = fields.Char(string='الدعوى', required=True)
    type = fields.Selection([
            ('1', '1'),
            ('2', '2'),
            ], string='التصنيف')
    
class retirement(models.Model):
    _name = 'retirement.type'
    _description = 'retirement types'
    
    name = fields.Char(string='الدعوى', required=True)
    type = fields.Selection([
            ('1', '1'),
            ('2', '2'),
            ], string='التصنيف')
    
class retirement(models.Model):
    _name = 'judicial.type'
    _description = 'retirement types'
    
    name = fields.Char(string='الدعوى', required=True)
    type = fields.Selection([
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ], string='التصنيف')
    
class retirement(models.Model):
    _name = 'fine.type'
    _description = 'retirement types'
    
    name = fields.Char(string='الدعوى', required=True)
    type = fields.Selection([
            ('6.1', '6.1'),
            ('6.2', '6.2'),
            ('6.3', '6.3'),
            ('6.4', '6.4'),
            ('6.5', '6.5'),
            ], string='التصنيف')
