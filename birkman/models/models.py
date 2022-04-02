# -*- coding: utf-8 -*-

from odoo import models, fields, api

class birkman(models.Model):
    _inherit = 'hr.employee'

    artistic = fields.Float(string='artistic', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    scientific = fields.Float(string='scientific', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    musical = fields.Float(string='musical', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    technical = fields.Float(string='technical', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    literary = fields.Float(string='literary', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    persuasive = fields.Float(string='persuasive', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    outdoor = fields.Float(string='outdoor', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    social_service = fields.Float(string='Social Service', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    administrative = fields.Float(string='administrative', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    numerical = fields.Float(string='numerical', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    birkman_image = fields.Image(string='خريطة بيركمان', groups="hr.group_hr_user")

    social_usual = fields.Float(string='social_usual', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    social_need = fields.Float(string='social_need', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    social_stress = fields.Float(string='social_stress', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    
    physical_usual = fields.Float(string='physical_usual', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    physical_need = fields.Float(string='physical_need', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    physical_stress = fields.Float(string='physical_stress', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")    
    
    emotional_usual = fields.Float(string='emotional_usual', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    emotional_need = fields.Float(string='emotional_need', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    emotional_stress = fields.Float(string='emotional_stress', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")    

    consciousness_usual = fields.Float(string='consciousness_usual', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    consciousness_need = fields.Float(string='consciousness_need', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    consciousness_stress = fields.Float(string='consciousness_stress', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")    

    assertiveness_usual = fields.Float(string='assertiveness_usual', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    assertiveness_need = fields.Float(string='assertiveness_need', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    assertiveness_stress = fields.Float(string='assertiveness_stress', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")    

    insistence_usual = fields.Float(string='insistence_usual', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    insistence_need = fields.Float(string='insistence_need', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    insistence_stress = fields.Float(string='insistence_stress', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")    

    incentives_usual = fields.Float(string='incentives_usual', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    incentives_need = fields.Float(string='incentives_need', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    incentives_stress = fields.Float(string='incentives_stress', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")    

    restlessness_usual = fields.Float(string='restlessness_usual', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    restlessness_need = fields.Float(string='restlessness_need', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    restlessness_stress = fields.Float(string='restlessness_stress', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")    

    thought_usual = fields.Float(string='thought_usual', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    thought_need = fields.Float(string='thought_need', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")
    thought_stress = fields.Float(string='thought_stress', default=0.0,  store=True, tracking=True, groups="hr.group_hr_user")    



