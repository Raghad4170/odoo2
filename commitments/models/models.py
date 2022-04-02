# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, datetime, date
from odoo.tools.misc import formatLang
import uuid


class Organization(models.Model):
    _name = 'commitments.organization'
    _description = 'المنظمات'

    name = fields.Char(string='المنظمة', required=True)
    systems_ids = fields.One2many('organization.systems', 'organization_id', string='الأنظمة')
    
class OrganizationSystems(models.Model):
    _name = 'organization.systems'
    _description = 'الأنظمة'

    name = fields.Char(string='النظام', required=True)
    organization_id = fields.Many2one('commitments.organization', string='المنظمة', required=True)
    types_ids = fields.One2many('organization.types', 'system_id', string='المجموعات')

    
class OrganizationTypes(models.Model):
    _name = 'organization.types'
    _description = 'النوع'

    name = fields.Char(string='الأسم')
    name_display = fields.Char(string='المجموعة', compute='_get_name_system')
    system_id = fields.Many2one('organization.systems', string='النظام')
    
    @api.depends('system_id','name')
    def _get_name_system(self):
        for types in self:
            if types.system_id and types.name:
                types.name_display = types.system_id.name + ' - ' + types.name
            else:
                types.name_display = types.name

class Activities(models.Model):
    _name = 'organization.activities'
    _description = 'الأنشطة الأساسية'

    name = fields.Char(string='الأنشطة الأساسية', required=True)
    supervizing = fields.Char(string='الجهة المشرفة', store=True)
    approval = fields.Char(string='الموافقات', store=True)
    activities_ids = fields.Many2many('activities.activities', string='الأنشطة المتجانسة')
    organization_systems = fields.Many2many('organization.systems', string='الأنظمة')

    organization_types = fields.Many2many('organization.types', string='المجموعات', compute='_get_organization_types', store=True, readonly=False)

 
    @api.depends('organization_systems')
    def _get_organization_types(self):
        for commitments in self:
            organization_types = []
            for systems in commitments.organization_systems:
                organization_types += systems.types_ids.ids
            commitments.organization_types = organization_types


    
class Activities(models.Model):
    _name = 'activities.activities'
    _description = 'الأنشطة المتجانسة'

    name = fields.Char(string='الأنشطة المتجانسة', required=True)

class Questions(models.Model):
    _name = 'commitments.questions'
    _description = 'المخالفات'

    name = fields.Text(string='المخالفة', required=True)
    organization_type = fields.Many2one('organization.types', string='المجموعة', required=True)
    fine = fields.Char(string='الغرامة', compute='_get_fine')
    notes = fields.Text(string='ملاحظات')
    fine_type = fields.Selection([
            ('محددة', 'محددة'),
            ('حد أدنى وأعلى', 'حد أدنى وأعلى'),
            ('جزاء', 'جزاء'),
            ('لا تزيد', 'لا تزيد'),
            ('اشتراط', 'اشتراط'),
            ('عقوبة', 'عقوبة'),
            ], string='نوع المخالفة', store=True, required=True)

    defineded_fine = fields.Float(string='الغرامة المحددة')
    high_fine = fields.Float(string='الحد الأعلى')
    low_fine = fields.Float(string='الحد الأدنى')
    penal = fields.Char(string='الجزاء')
    
    @api.depends('fine_type','defineded_fine','high_fine','low_fine','penal')
    def _get_fine(self):
        for questions in self:
            fine = False
            defineded_fine = formatLang(self.env, questions.defineded_fine)
            high_fine = formatLang(self.env, questions.high_fine)
            low_fine = formatLang(self.env, questions.low_fine)

            if questions.fine_type == 'محددة':
                fine = defineded_fine
            elif questions.fine_type == 'حد أدنى وأعلى':
                fine = 'من ' + low_fine + ' إلى ' + high_fine
            elif questions.fine_type == 'لا تزيد':
                fine =  'لا تزيد على ' + high_fine
            elif questions.fine_type == 'جزاء':
                fine = defineded_fine + '، ' + str(questions.penal)
            elif questions.fine_type == 'عقوبة':
                fine = str(questions.penal)
            elif questions.fine_type == 'اشتراط':
                fine = 'اشتراط'
            questions.fine = fine

class Line(models.Model):
    _name = 'commitments.line'
    _description = 'مقدار الالتزام'
    
    name = fields.Text(string='تبرير عدم الإلتزام')
    commitments_id = fields.Many2one('company.commitments', string='الالتزام')
    questions_id = fields.Many2one('commitments.questions', string='المخالفة', auto_join=True)
    organization_type = fields.Many2one('organization.types', string='المجموعة')
    question = fields.Text(related='questions_id.name')
    fine = fields.Text(string='الغرامة', compute='_get_fine', store=True)
    notes = fields.Text(string='ملاحظات', compute='_get_notes', store=True)
    commitment_type = fields.Selection([
            ('ملتزم', 'ملتزم'),
            ('غير ملتزم', 'غير ملتزم'),
            ], string='الالتزام', store=True)
    sequence_no = fields.Integer('No.', compute="_sequence_no")
    display_type = fields.Selection([
    ('line_section', "Section"),
    ('line_note', "Note")], default=False, help="Technical field for UX purpose.") 
    is_answered = fields.Boolean('Is Answered',default=False, store=True)


    @api.depends('commitment_type')
    def _get_fine(self):
        for line in self:
            if line.questions_id.fine:
                if line.commitment_type == 'غير ملتزم':
                    line.fine = line.questions_id.fine
                else:
                    line.fine = ''
                    
    @api.depends('questions_id')
    def _get_notes(self):
        for line in self:
            if line.questions_id.notes:
                line.notes = line.questions_id.notes

    @api.depends('commitments_id.commitments_line.questions_id')
    def _sequence_no(self):
        for line in self:
            no = 0
            for l in line.commitments_id.commitments_line:
                if l.commitment_type == 'غير ملتزم':
                    no += 1
                    l.sequence_no = no
                else:
                    l.sequence_no = no
                    

class Company(models.Model):
    _name = 'company.commitments'
    _description = 'الالتزام'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    
    def preview_commitments(self):
        self.ensure_one()
        base_url = self.company_id.website
        portal_url = base_url + '/company_commitments/' + str(self.id) + '?access_token=' + str(self.access_token)
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': portal_url,
        }    
    
    
    def get_portal_url_pdf_download(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        self.ensure_one()
        base_url = self.company_id.website
        access_url = base_url + '/commitments_print/' + str(self.id)
        url = access_url + '%s?access_token=%s%s%s%s%s' % (
            suffix if suffix else '',
            self.access_token,
            '&report_type=%s' % report_type if report_type else '',
            '&download=true' if download else '',
            query_string if query_string else '',
            '#%s' % anchor if anchor else ''
        )
        return url
    
    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s' % (self.name)

    def _default_access_token(self):
        return str(uuid.uuid4())
    
    access_token = fields.Char('Security Token', required=True, default=_default_access_token, readonly=True)
    
    name = fields.Char(string='الالتزام', compute='_get_the_name')
    date = fields.Date(string='التاريخ', default=date.today(), required=True)
    partner_id = fields.Many2one('res.partner', string='العميل', required=True)
    user_id = fields.Many2one('res.users', string='المسؤول', default=lambda self: self.env.user, required=True)
    company_id = fields.Many2one(related='user_id.company_id')
    commitments_line = fields.One2many('commitments.line', 'commitments_id', string='مقدار الالتزام', compute='_get_commitments_line', store=True, readonly=False)
    organization_types = fields.Many2many('organization.types', string='المجموعة', compute='_get_organization_types', readonly=False, store=True)
    activities_ids = fields.Many2many('organization.activities', related='partner_id.activities_ids', string='الأنشطة', readonly=False)
    report = fields.Text(string='المخالفات', compute='_get_details', store=True, readonly=True)
    fines = fields.Float(string='مجموع الغرامات', compute='_get_details', store=True, readonly=True)
    fine_numbers = fields.Integer(string='عدد المخالفات', compute='_get_details', store=True, readonly=True)
    commitments_percentage = fields.Text(string='نسبة الالتزام', compute='_get_details', store=True, readonly=True)
    
    def _get_the_name(self):
        for commitments in self:
            if commitments.partner_id and commitments.date:
                commitments.name = 'التزام ' + commitments.partner_id.name + ' يوم ' + str(commitments.date)
                
                
    is_answered = fields.Boolean(compute='_check_is_answered')
    
    
    def _check_is_answered(self):
        for commitments in self:
            is_answered = False
            answered = 0
            line_no = 0
            for line in commitments.commitments_line:
                if line.display_type != 'line_section':
                    line_no += 1
                    if line.commitment_type:
                        answered += 1
            line_answered = (answered / line_no) * 100
            if line_answered == 100:
                is_answered = True
            commitments.is_answered = is_answered
            

    @api.depends('activities_ids')
    def _get_organization_types(self):
        for commitments in self:
            organization_types = []
            for activities in commitments.activities_ids:
                organization_types += activities.organization_types.ids
            commitments.organization_types = organization_types

    @api.model
    def create(self, vals):
        res = super(Company, self).create(vals)
        organization_types = []
        for activities in res.activities_ids:
            organization_types += activities.organization_types.ids
        res.write({'organization_types':organization_types})
        return res

    @api.depends('organization_types')
    def _get_commitments_line(self):
        for commitments in self:
            data_line = []
            data = []
            organizations = commitments.organization_types.ids
            not_commitments = self.env['commitments.line'].sudo().search([('commitments_id','=', commitments.id),('organization_type','not in', organizations)])
            not_commitments.unlink()
            question_line = commitments.commitments_line.questions_id.ids
            for organization in commitments.organization_types:
                questions_ids = self.env['commitments.questions'].sudo().search([('organization_type','=', organization.id),('id','not in', question_line)])
                if len(questions_ids):
                    data_line = [(0, 0, {
                            'name': organization.name_display,
                            'organization_type': organization.id,
                            'display_type':'line_section'
                            })]
                    commitments.commitments_line = data_line
                for question in questions_ids:
                    data = [(0, 0, {
                                    'questions_id': question.id,
                                    'organization_type': question.organization_type.id,
                                    'display_type':False

                                    })]
                    commitments.commitments_line = data
                
                
    @api.depends('commitments_line.commitment_type','activities_ids')
    def _get_details(self):
        for commitments in self:
            report = ''
            line_number = 0
            fine = 0
            fines = 0
            commitment_number = 0
            all = 0
            fine_numbers = 0
            for line in commitments.commitments_line:
                if line.display_type != 'line_section':
                    line_number += 1
                    if line.commitment_type == 'غير ملتزم':
                        commitment_number += 0
                        fine_numbers += 1
                        if line.fine:
                            notes = ""
                            if line.notes:
                                notes = '\n' + 'ملاحظات: ' + str(line.notes)
                            report += str (line.sequence_no) + '- ' + 'المخالفة: ' + str(line.question) + notes + '\n' + 'الغرامة: ' +  str(line.fine) + '\n' + '\n'
                        if line.questions_id.fine_type == 'حد أدنى وأعلى':
                            fine += line.questions_id.high_fine
                        else:
                            fine += line.questions_id.defineded_fine
                    elif line.commitment_type == 'ملتزم':
                        commitment_number += 1
                        fine_numbers += 0
                        
            all += commitment_number
            line_numbers = line_number
            percentage = (all / (line_numbers or 1) ) * 100
            percentage_round = round(percentage, 2)
            commitments.commitments_percentage = percentage_round
            
            fines += fine
            commitments.fines = fines
            commitments.fine_numbers = fine_numbers
            commitments.report = report
            
class partnerinfo(models.Model):
    _inherit = "res.partner"

    activities_ids = fields.Many2many('organization.activities', string='الأنشطة')


