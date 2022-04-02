# Copyright to The City Law Firm
from odoo import models, fields, api
from datetime import datetime, time


class HrViolations(models.Model):

    _name = 'violations.type'
    _description = 'violations.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='المخالفة',required=True)
    
    First_time = fields.Selection([
        ('انذار كتابي', 'انذار كتابي'),
        ('نسبة مئوية','نسبة مئوية'),
        ('يوم', 'يوم'),
        ('اخرى','اخرى')],required=True,string ='المرة الأولى',default='انذار كتابي')
   
    violation_type = fields.Selection([('late_15m','late_15m'),('late_15m_2','late_15m_2'),('late_30m','late_30m'),('late_30m_2','late_30m_2'),('late_60m','late_60m'),('late_60m_2','late_60m_2'),('late_more_60m','late_more_60m'),('early_15','early_15'),('early_more_15','early_more_15'),('absence','absence')],string ='violation Type')    
    First_penality= fields.Float(string='الجزاء الأول')
    First_other= fields.Char(string='المخالفة الأولى')
    Second_Time = fields.Selection([
        ('انذار كتابي', 'انذار كتابي'),
        ('نسبة مئوية','نسبة مئوية'),
        ('يوم', 'يوم'),
        ('اخرى','اخرى')],string ='المرة الثانية',default='انذار كتابي')
    Second_penality= fields.Float(string='الجزاء الثاني')
    Second_other= fields.Char(string='المخالفة الثانية')
    Third_time= fields.Selection([
        ('انذار كتابي', 'انذار كتابي'),
        ('نسبة مئوية','نسبة مئوية'),
        ('يوم', 'يوم'),
        ('اخرى','اخرى')],string ='المرة الثالثة',default='انذار كتابي')
    Third_penality= fields.Float(string='الجزاء الثالث')
    Third_other= fields.Char(string='المخالفة الثالثة')
    Fourth_time= fields.Selection([
        ('انذار كتابي', 'انذار كتابي'),
        ('نسبة مئوية','نسبة مئوية'),
        ('يوم', 'يوم'),
        ('اخرى','اخرى')],string ='المرة الرابعة',default='انذار كتابي')
    Fourth_penality= fields.Float(string='الجزاء الرابع')
    Fourth_other= fields.Char(string='المخالفة الرابعة')
