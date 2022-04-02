# -*- coding: utf-8 -*-

from collections import OrderedDict
from operator import itemgetter
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import Website
import json
import base64
from odoo.osv.expression import OR
import pytz
from datetime import datetime, timedelta, date

class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'litigation_count' in counters:
            values['litigation_count'] = request.env['litigation.litigation'].search_count([])
        if 'consulting_count' in counters:
            values['consulting_count'] = request.env['consulting.consulting'].search_count([])
        if 'contractconsulting_count' in counters:
            values['contractconsulting_count'] = request.env['contractconsulting.contractconsulting'].search_count([])
        return values

    # ------------------------------------------------------------
    # My litigation
    # ------------------------------------------------------------
    def _litigation_get_page_view_values(self, litigation, access_token, **kwargs):
        values = {
            'page_name': 'litigation',
            'litigation': litigation,
        }
        return self._get_page_view_values(litigation, access_token, values, 'my_litigations_history', False, **kwargs)

    @http.route(['/my/litigations', '/my/litigations/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_litigations(self, page=1, date_begin=None, date_end=None, search=None, search_in='all', sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        litigation = request.env['litigation.litigation']
        domain = []
        
        
        searchbar_filters = {
            'ongoing': {'label': _('قضايا قيد التنفيذ'), 'domain': [('litigation_state', '!=', ('انتهت بحكم قضائي','انتهت صلحاً','انتهت'))]},
            'finished': {'label': _('قضايا منتهية'), 'domain': [('litigation_state', '=', ('انتهت بحكم قضائي','انتهت صلحاً','انتهت'))]},
            'all': {'label': _('الكل'), 'domain': []},

        }
        
        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('البحث في الكل')},
            'name': {'input': 'name', 'label': _('البحث في القضية')},
            'client_state': {'input': 'client_state', 'label': _('البحث في صفة الموكل')},
            'litigation_number': {'input': 'litigation_number', 'label': _('البحث في رقم القضية')},
            'court': {'input': 'court', 'label': _('البحث في المحكمة')},
        }
        
        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('litigation_number', 'all'):
                search_domain = OR([search_domain, [('litigation_number', 'ilike', search)]])
            if search_in in ('court', 'all'):
                search_domain = OR([search_domain, [('court', 'ilike', search)]])
            if search_in in ('client_state', 'all'):
                search_domain = OR([search_domain, [('client_state', 'ilike', search)]])
            domain += search_domain

        
        searchbar_sortings = {
            'date': {'label': _('الأحدث'), 'order': 'next_court_date desc', 'domain': [('next_court_date', '!=', False)]},
            'name': {'label': _('صفة الموكل'), 'order': 'client_state'},
            'litigation_state': {'label': _('حالة القضية'), 'order': 'litigation_state'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain']
        
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # litigation count
        litigation_count = litigation.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/litigations",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'search_in': search_in, 'filterby': filterby, 'sortby': sortby},
            total=litigation_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        litigations = litigation.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_litigations_history'] = litigations.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'litigations': litigations,
            'page_name': 'litigation',
            'default_url': '/my/litigations',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'filterby': filterby,
        })
        return request.render("litigation.portal_my_litigations", values)

    @http.route(['/my/litigation/<int:litigation_id>'], type='http', auth="public", website=True)
    def portal_my_litigation(self, litigation_id=None, access_token=None, **kw):
        try:
            litigation_sudo = self._document_check_access('litigation.litigation', litigation_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._litigation_get_page_view_values(litigation_sudo, access_token, **kw)
        return request.render("litigation.portal_my_litigation", values)    

    @http.route(['/my/litigation_print/<int:litigation_id>'], type='http', auth="public", website=True)
    def print_litigation_xml(self, litigation_id=None, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access(
                'litigation.litigation', litigation_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            template = 'litigation.action_report_litigation'
            return self._show_report(model=order_sudo, report_type=report_type, report_ref=template, download=download)

    # ------------------------------------------------------------
    # My consulting
    # ------------------------------------------------------------
    def _consulting_get_page_view_values(self, consulting, access_token, **kwargs):
        values = {
            'page_name': 'consulting',
            'consulting': consulting,
        }
        return self._get_page_view_values(consulting, access_token, values, 'my_consultings_history', False, **kwargs)

    @http.route(['/my/consultings', '/my/consultings/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_consultings(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        consulting = request.env['consulting.consulting']
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # consulting count
        consulting_count = consulting.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/consultings",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=consulting_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        consultings = consulting.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_consultings_history'] = consultings.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'consultings': consultings,
            'page_name': 'consulting',
            'default_url': '/my/consultings',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("litigation.portal_my_consultings", values)

    @http.route(['/my/consulting/<int:consulting_id>'], type='http', auth="public", website=True)
    def portal_my_consulting(self, consulting_id=None, access_token=None, **kw):
        try:
            consulting_sudo = self._document_check_access('consulting.consulting', consulting_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._consulting_get_page_view_values(consulting_sudo, access_token, **kw)
        return request.render("litigation.portal_my_consulting", values)

    @http.route(['/my/consulting_print/<int:consulting_id>'], type='http', auth="public", website=True)
    def print_consulting_xml(self, consulting_id=None, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access(
                'consulting.consulting', consulting_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            template = 'litigation.action_report_consulting'
            return self._show_report(model=order_sudo, report_type=report_type, report_ref=template, download=download)

    # ------------------------------------------------------------
    # My contract consulting
    # ------------------------------------------------------------
    def _contractconsulting_get_page_view_values(self, contractconsulting, access_token, **kwargs):
        values = {
            'page_name': 'contractconsulting',
            'contractconsulting': contractconsulting,
        }
        return self._get_page_view_values(contractconsulting, access_token, values, 'my_contractconsultings_history', False, **kwargs)

    @http.route(['/my/contractconsultings', '/my/contractconsultings/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_contractconsultings(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        contractconsulting = request.env['contractconsulting.contractconsulting']
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # contractconsulting count
        contractconsulting_count = contractconsulting.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/contractconsultings",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=contractconsulting_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        contractconsultings = contractconsulting.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_contractconsultings_history'] = contractconsultings.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'contractconsultings': contractconsultings,
            'page_name': 'contractconsulting',
            'default_url': '/my/contractconsultings',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("litigation.portal_my_contractconsultings", values)

    @http.route(['/my/contractconsulting/<int:contractconsulting_id>'], type='http', auth="public", website=True)
    def portal_my_contractconsulting(self, contractconsulting_id=None, access_token=None, **kw):
        try:
            contractconsulting_sudo = self._document_check_access('contractconsulting.contractconsulting', contractconsulting_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._contractconsulting_get_page_view_values(contractconsulting_sudo, access_token, **kw)
        return request.render("litigation.portal_my_contractconsulting", values)

    
    
    
    # ------------------------------------------------------------
    # Portal Rating
    # ------------------------------------------------------------
    # litigation report_ids

    @http.route(['/generate_tab_data'],  type='json', auth="public", methods=['POST'], website=True)
    def generate_tab_data(self,litigation_id):
        litigation_data=request.env['litigation.litigation'].sudo().browse(int(litigation_id))
        lit_list=[]
        lit_dic={}
        old_tz = pytz.timezone('UTC')
        new_tz = pytz.timezone(request.env.user.tz)

        if litigation_data.report_ids:
            for rpt in litigation_data.report_ids:
                lit_dic['id']=rpt.id
                lit_dic['name']=rpt.name
                lit_dic['summary']=rpt.summary
                lit_dic['court_date']= old_tz.localize(rpt.court_date).astimezone(new_tz)
                lit_dic['court_type']=rpt.court_type
                lit_dic['present_judges']=rpt.present_judges
                lit_dic['writer']=rpt.writer
                lit_dic['link']=rpt.link
                lit_list.append(lit_dic)
                lit_dic={}
        return lit_list

    
    # litigation Rating

    @http.route(['/litigation_rating'],  type='json', auth="public", methods=['POST'], website=True)
    def litigation_rating(self,litigation_id):
        return request.env['litigation.litigation'].browse(int(litigation_id)).customer_rating

    @http.route(['/close_litigation_fivestar'],  type='json', auth="public", methods=['POST'], website=True)
    def close_litigation_fivestar(self,litigation_id):
        User = request.env.user
        if User.user_has_groups('base.group_portal'):
            request.env['litigation.litigation'].sudo().browse(int(litigation_id)).sudo().write({'customer_rating':'5'})
            return True
        else:
            return False

    @http.route(['/close_litigation_less_fivestar'],  type='json', auth="public", methods=['POST'], website=True)
    def close_litigation_less_fivestar(self,litigation_id,response,rating):
        User = request.env.user
        if User.user_has_groups('base.group_portal'):
            request.env['litigation.litigation'].sudo().browse(int(litigation_id)).sudo().write({'customer_response':response,'customer_rating':rating})
            return True
        else:
            return  False

    # consulting Rating
    @http.route(['/consulting_state'],  type='json', auth="public", methods=['POST'], website=True)
    def consulting_state(self,consulting_id):
        return request.env['consulting.consulting'].browse(int(consulting_id)).state
         
    @http.route(['/consulting_rating'],  type='json', auth="public", methods=['POST'], website=True)
    def consulting_rating(self,consulting_id):
        return request.env['consulting.consulting'].browse(int(consulting_id)).customer_rating

    @http.route(['/close_consulting_fivestar'],  type='json', auth="public", methods=['POST'], website=True)
    def close_consulting_fivestar(self,consulting_id):
        User = request.env.user
        if User.user_has_groups('base.group_portal'):
            request.env['consulting.consulting'].browse(int(consulting_id)).sudo().write({'customer_rating':'5'})
        else:
            return False

    @http.route(['/close_consulting_less_fivestar'],  type='json', auth="public", methods=['POST'], website=True)
    def close_consulting_less_fivestar(self,consulting_id,response,rating,close_bool):
        User = request.env.user
        if User.user_has_groups('base.group_portal'):
            request.env['consulting.consulting'].sudo().browse(int(consulting_id)).sudo().write({'customer_response':response,'customer_rating':rating})
        else:
            return False

    @http.route(['/visblity_close_button_consulting'],  type='json', auth="public", methods=['POST'], website=True)
    def visblity_close_button_consulting(self,consulting_id):
        User = request.env.user
        if User.user_has_groups('base.group_portal'):
            request.env['consulting.consulting'].sudo().browse(int(consulting_id)).write({'state':'close'})
        else:
            return False      

    # contractconsulting Rating
    @http.route(['/contra_consulting_state'],  type='json', auth="public", methods=['POST'], website=True)
    def contra_consulting_state(self,contractconsulting_id):
        return request.env['contractconsulting.contractconsulting'].browse(int(contractconsulting_id)).state

    @http.route(['/visblity_close_button_contra_consulting'],  type='json', auth="public", methods=['POST'], website=True)
    def visblity_close_button_contra_consulting(self,contractconsulting_id):
        User = request.env.user
        if User.user_has_groups('base.group_portal'):
            request.env['contractconsulting.contractconsulting'].sudo().browse(int(contractconsulting_id)).write({'state':'close'})
        else:
            return False      



    @http.route(['/contractconsulting_rating'],  type='json', auth="public", methods=['POST'], website=True)
    def contractconsulting_rating(self,contractconsulting_id):
        return request.env['contractconsulting.contractconsulting'].browse(int(contractconsulting_id)).customer_rating        


    @http.route(['/close_contractconsulting_fivestar'],  type='json', auth="public", methods=['POST'], website=True)
    def close_contractconsulting_fivestar(self,contractconsulting_id):
        User = request.env.user
        if User.user_has_groups('base.group_portal'):
            request.env['contractconsulting.contractconsulting'].sudo().browse(int(contractconsulting_id)).sudo().write({'customer_rating':'5'})
        else:
            return False      


    @http.route(['/close_contractconsulting_less_fivestar'],  type='json', auth="public", methods=['POST'], website=True)
    def close_contractconsulting_less_fivestar(self,contractconsulting_id,response,rating,close_bool):
        User = request.env.user
        if User.user_has_groups('base.group_portal'):
            request.env['contractconsulting.contractconsulting'].sudo().browse(int(contractconsulting_id)).sudo().write({'customer_response':response,'customer_rating':rating})
        else:
            return False

    @http.route(['/visblity_close_button_contractconsulting'],  type='json', auth="public", methods=['POST'], website=True)
    def visblity_close_button_contractconsulting(self,contractconsulting_id):
        if request.env['contractconsulting.contractconsulting'].sudo().browse(int(contractconsulting_id)).state=='close':
            return False
        else:
            return True
        
        
        
#         company document
        
    def _document_get_page_view_values(self, document, access_token, **kwargs):
        values = {
            'page_name': 'document',
            'document': document,
        }
        return self._get_page_view_values(document, access_token, values, 'my_documents_history', False, **kwargs)

        
    @http.route(['/company_document/<int:document_id>'], type='http', auth="public", website=True)
    def portal_company_document(self, document_id=None, access_token=None, **kw):
        try:
            document_sudo = self._document_check_access('company.document', document_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
 
        values = self._document_get_page_view_values(document_sudo, access_token, **kw)
        return request.render("litigation.portal_company_document", values) 
    
    
    @http.route(['/my/company_document_print/<int:document_id>'], type='http', auth="public", website=True)
    def print_document_xml(self, document_id=None, report_type=None, access_token=None, message=False, download=False, **kw):
        document_sudo = self._document_check_access('company.document', document_id, access_token=access_token)
        if report_type in ('html', 'pdf', 'text'):
            template = 'litigation.action_company_document'
            return self._show_report(model=document_sudo, report_type=report_type, report_ref=template, download=download)

