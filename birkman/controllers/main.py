import base64
import json

from odoo import http, SUPERUSER_ID, _
from odoo.http import request
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.form import WebsiteForm
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
import dateutil
from dateutil.relativedelta import relativedelta

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import logging
_logger = logging.getLogger(__name__)

class CustomerPortal(CustomerPortal):

    # ------------------------------------------------------------
    # My brikman
    # ------------------------------------------------------------
    def _brikman_get_page_view_values(self, brikman, access_token, **kwargs):
        values = {
            'page_name': 'اختبار بيركمان',
            'brikman': brikman,
        }
        return self._get_page_view_values(brikman, access_token, values, 'my_brikmans_history', False, **kwargs)

    @http.route(['/my/birkmans', '/my/birkmans/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_birkmans(self, page=1, date_begin=None, date_end=None, **kw):
        values = self._prepare_portal_layout_values()
        birkman = request.env['birkman']
        domain = []

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # brikman count
        brikman_count = birkman.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/birkmans",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=brikman_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        birkmans = birkman.search(domain, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_brikmans_history'] = birkmans.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'birkmans': birkmans,
            'page_name': 'birkman',
            'default_url': '/my/birkmans',
            'pager': pager,
        })
        
        return request.render("birkman.birkman_list", values)

    
    @http.route(['/my/birkman/<int:birkman_id>'], type='http', auth="public", website=True)
    def portal_my_birkman(self,birkman_id=None, access_token=None, **kw):
        try:
            brikman_sudo = self._document_check_access('birkman', birkman_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._brikman_get_page_view_values(brikman_sudo, access_token, **kw)
        return request.render("birkman.brikman_brikman_followup", values)
    
        

class WebsiteSaleForm(WebsiteForm):
  
         

    @http.route(['/submit_birkman'], type='http', auth="public", website=True)
    def submit_birkman(self,**kwargs):
        service_type_obj=request.env['birkman.serivce.type']

        result={}
   
        service_types = service_type_obj.sudo().search([])
        result['service_type_ids'] = service_types        

        if request.env.user.has_group('base.group_public') == False:
            result['partner_id'] = request.env.user.partner_id.id    
            result['email'] = request.env.user.partner_id.email        
            result['partner'] = request.env.user.partner_id.name  
            result['phone'] = request.env.user.partner_id.phone    

        return request.render("birkman.birkman_submit_form", result)


    @http.route(['/save_birkman'], type='http',csrf=False, auth="public", website=True)
    def save_birkman(self,**kw):
        birkman_obj=request.env['birkman']
        partner_obj = request.env['res.partner']
        user_obj=request.env['res.users']

        if kw.get('service_type_id',False):
            kw['service_type_id']=int(kw['service_type_id'])


        if kw.get('partner_id',False):
            kw['partner_id']=int(kw['partner_id'])

        if kw.get('qty',False):
            kw['qty']=int(kw['qty'])

        result={}

        if request.env.user.has_group('base.group_public'):
            user_id=user_obj.sudo().create({'login':kw['email'],'password':kw['phone'],'name':kw['partner'],'groups_id':[]})
            group_portal = request.env.ref('base.group_portal')
            group_portal.sudo().write({'users': [(4, user_id.id)]})
            user_id.partner_id.sudo().write({'email':kw['email'],'phone':kw['phone']})

            kw['partner_id'] = user_id.partner_id.id
            result['public_user'] = True
        else:
            result['public_user']= False



        internal_id=birkman_obj.sudo().create(kw)

        all_ids=birkman_obj.search([('partner_id','=',request.env.user.partner_id.id)])
        list_r = []
        for browse_rec in all_ids:
            list_r.append(browse_rec)
      

        result['internal_slate']=list_r
        
        result['sale_url'] = internal_id.sale_url
        result['portal_url'] = internal_id.portal_url
        return request.render("birkman.birkman_submit_msg", result)