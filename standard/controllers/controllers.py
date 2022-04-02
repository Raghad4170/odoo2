from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import Website
import re

class CustomerPortal(CustomerPortal):

    def _standard_get_page_view_values(self, standard, access_token, **kwargs):
        values = {
            'page_name': 'النماذج الموحدة',
            'standard': standard,
        }
        return self._get_page_view_values(standard, access_token, values, 'my_standards_history', False, **kwargs)

    @http.route(['/my/standards', '/my/standards/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_standards(self, page=1, date_begin=None, date_end=None, **kw):
        values = self._prepare_portal_layout_values()
        standard = request.env['standard.standard']
        domain = []

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # standard count
        standard_count = standard.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/standards",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=standard_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        standards = standard.search(domain, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_standards_history'] = standards.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'standards': standards,
            'page_name': 'standard',
            'default_url': '/my/standards',
            'pager': pager,
        })
        return request.render("standard.standard_portal_list", values)

    @http.route(['/my/standards/<int:standard_id>/sign'], type='json', auth="public", website=True)
    def portal_accept_sign(self, standard_id, access_token=None, name=None, signature=None,sign_name=None):
        standard = request.env['standard.standard']
        partner_obj = request.env['res.partner']
        standard_replace = request.env['standard.replace']
        data=standard.browse(int(standard_id))
        clean = re.compile('<.*?>')   
        standard_text=data.standard_id.Text
        all_text=re.sub(clean, '', standard_text).split(' ')
        for text_each in all_text: 
            replace_ids = standard_replace.search([('replace','ilike',re.sub(clean, '', text_each)),('standards','=','sign')])

            if len(replace_ids):
                for replace_id in replace_ids:
                    idrec=replace_id[0].id
                    partner_one=standard.search([('id','=',data.id),('x_'+str(idrec),'=',request.env.user.partner_id.id)])
                    if len(partner_one):
                        data.write({'x_sign_'+str(idrec):signature,'x_sign_name_'+str(idrec):sign_name})

        return {'force_refresh': True}
 

    @http.route(['/my/standard/<int:standard_id>'], type='http', auth="public", website=True)
    def portal_my_standard(self, standard_id=None, access_token=None, **kw):
        try:
            standard_sudo = self._document_check_access('standard.standard', standard_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._standard_get_page_view_values(standard_sudo, access_token, **kw)
        
        
        values['sign_user'] = False

        standard = request.env['standard.standard']
        partner_obj = request.env['res.partner']
        standard_replace = request.env['standard.replace']
        data=standard.browse(int(standard_id))
        clean = re.compile('<.*?>')   
        standard_text=data.standard_id.Text
        all_text=re.sub(clean, '', standard_text).split(' ')
        for text_each in all_text: 
            replace_ids = standard_replace.search([('replace','ilike',re.sub(clean, '', text_each)),('standards','=','sign')])

            if len(replace_ids):
                for replace_id in replace_ids:
                    idrec=replace_id[0].id
                    partner_one=standard.search([('id','=',data.id),('x_'+str(idrec),'=',request.env.user.partner_id.id)])
                    if len(partner_one):
                        values['sign_user'] = True

        return request.render("standard.standard_portal", values)
    
    @http.route(['/standard_print/<int:standard_id>'], type='http', auth="public", website=True)
    def print_standard_xml(self, standard_id=None, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access('standard.standard', standard_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            template = 'standard.action_report_standard'
            return self._show_report(model=order_sudo, report_type=report_type, report_ref=template, download=download)


        
        
        
        
#         standard contract


    def _standardcontract_get_page_view_values(self, standardcontract, access_token, **kwargs):
        values = {
            'page_name': 'العقود الموحدة',
            'standardcontract': standardcontract,
        }
        return self._get_page_view_values(standardcontract, access_token, values, 'my_standardcontracts_history', False, **kwargs)

    @http.route(['/my/standardcontracts', '/my/standardcontracts/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_standardcontracts(self, page=1, date_begin=None, date_end=None, **kw):
        values = self._prepare_portal_layout_values()
        standardcontract = request.env['contract.standard']
        domain = []

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # standardcontract count
        standardcontract_count = standardcontract.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/standardcontracts",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=standardcontract_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        standardcontracts = standardcontract.search(domain, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_standardcontracts_history'] = standardcontracts.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'standardcontracts': standardcontracts,
            'page_name': 'standard',
            'default_url': '/my/standardcontracts',
            'pager': pager,
        })
        return request.render("standard.standardcontract_portal_list", values)
    
    
    @http.route(['/my/standardcontract/<int:standardcontract_id>'], type='http', auth="public", website=True)
    def portal_my_standardcontract(self, standardcontract_id=None, access_token=None, **kw):

        try:
            standardcontract_sudo = self._document_check_access('contract.standard', standardcontract_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._standardcontract_get_page_view_values(standardcontract_sudo, access_token, **kw)
        
        values['sign_user'] = False
        standardcontract = request.env['contract.standard']
        data = standardcontract.browse(int(standardcontract_id))
        if (data.first_side.id or data.second_side.id or data.first_witness.id or data.second_witness.id)  == request.env.user.partner_id.id  :
            values['sign_user'] = True

        return request.render("standard.standardcontract_portal", values)


    @http.route(['/my/standardcontracts/<int:standardcontract_id>/sign'], type='json', auth="public", website=True)
    def portal_accept_sign_contract(self, standardcontract_id, access_token=None, name=None, signature=None,sign_name=None):        
        standardcontract = request.env['contract.standard']
        data=standardcontract.browse(int(standardcontract_id))
        if data.first_side.id == request.env.user.partner_id.id:
            data.write({'first_side_sign':signature,'first_side_sign_name':sign_name})
        if data.second_side.id == request.env.user.partner_id.id:
            data.write({'second_side_sign':signature,'second_side_sign_name':sign_name})
        if data.first_witness.id == request.env.user.partner_id.id:
            data.write({'first_witness_sign':signature,'first_witness_sign_name':sign_name})    
        if data.second_witness.id == request.env.user.partner_id.id:
            data.write({'second_witness_sign':signature,'second_witness_sign_name':sign_name})    
          
        return {'force_refresh': True}

    
    @http.route(['/standardcontract_print/<int:standardcontract_id>'], type='http', auth="public", website=True)
    def print_standardcontract_xml(self, standardcontract_id=None, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access('contract.standard', standardcontract_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            template = 'standard.action_report_contract_standard'
            return self._show_report(model=order_sudo, report_type=report_type, report_ref=template, download=download)

