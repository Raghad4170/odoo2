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

class CustomerPortal(CustomerPortal):

    # ------------------------------------------------------------
    # My slate
    # ------------------------------------------------------------
    def _slate_get_page_view_values(self, slate, access_token, **kwargs):
        values = {
            'page_name': 'لائحة العمل الداخلية',
            'slate': slate,
        }
        return self._get_page_view_values(slate, access_token, values, 'my_slates_history', False, **kwargs)

    @http.route(['/my/slates', '/my/slates/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_slates(self, page=1, date_begin=None, date_end=None, **kw):
        values = self._prepare_portal_layout_values()
        slate = request.env['internal.slate']
        domain = []

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # slate count
        slate_count = slate.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/slates",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=slate_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        slates = slate.search(domain, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_slates_history'] = slates.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'slates': slates,
            'page_name': 'slate',
            'default_url': '/my/slates',
            'pager': pager,
        })
        return request.render("Internal_slate.internal_slate_list", values)

    
    @http.route(['/my/slate/<int:slate_id>'], type='http', auth="public", website=True)
    def portal_my_slate(self, slate_id=None, access_token=None, **kw):
        try:
            slate_sudo = self._document_check_access('internal.slate', slate_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._slate_get_page_view_values(slate_sudo, access_token, **kw)
        return request.render("Internal_slate.internal_slate_followup", values)
    
    
    @http.route(['/slate_print/<int:slate_id>'], type='http', auth="public", website=True)
    def print_slate_xml(self, slate_id=None, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access('internal.slate', slate_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            template = 'Internal_slate.action_report_internal_slate'
            return self._show_report(model=order_sudo, report_type=report_type, report_ref=template, download=download)

        

class WebsiteSaleForm(WebsiteForm):
    

    @http.route("/get_date", type='json', auth="public", website=True)
    def get_date(self,slate_id):
        internal_slate_obj=request.env['internal.slate']
        try:
            m=int(slate_id)
        except:
            return False
        data=internal_slate_obj.search([('id','=',m)])
        if len(data):
            return data.service_date
         

    @http.route(['/submit_slates'], type='http', auth="public", website=True)
    def submit_slates(self,**kwargs):
        service_type_obj=request.env['serivce.type']

        result={}
   
        service_types = service_type_obj.sudo().search([])
        result['service_type_ids'] = service_types        

        if request.env.user.has_group('base.group_public') == False:
            result['partner_id'] = request.env.user.partner_id.id    
            result['email'] = request.env.user.partner_id.email        
            result['partner'] = request.env.user.partner_id.name  
            result['phone'] = request.env.user.partner_id.phone
            
        if request.env.user.has_group('base.group_public') == False:
            if request.env.user.partner_id.parent_id:
                result['partner_company'] = request.env.user.partner_id.parent_id.name    


        return request.render("Internal_slate.internal_slate_submit_form", result)


    @http.route(['/save_slates'], type='http',csrf=False, auth="public", website=True)
    def save_slates(self,**kw):
        internal_slate_obj=request.env['internal.slate']
        partner_obj = request.env['res.partner']
        user_obj=request.env['res.users']

        if kw.get('service_type_id',False):
            kw['service_type_id']=int(kw['service_type_id'])

        if kw.get('partner_company',False):
            partner_company = request.env['res.partner'].sudo().create({'name':kw['partner_company']})
            kw['partner_company'] = partner_company.id

        if kw.get('partner_id',False):
            kw['partner_id']=int(kw['partner_id'])
        result={}

        if request.env.user.has_group('base.group_public'):
            if request.env["res.users"].sudo().search([("login", "=", kw['email'])]):  
                raise AccessError(('يوجد لدينا مستخدم بنفس بيانات مقدم الطلب، نأمل منكم رفع الطلب بعد تسجيل الدخول.'))
            else:
                user_id=user_obj.sudo().create({'login':kw['email'],'password':kw['phone'],'name':kw['partner'],'groups_id':[]})
                group_portal = request.env.ref('base.group_portal')
                group_portal.sudo().write({'users': [(4, user_id.id)]})
                user_id.partner_id.sudo().write({'email':kw['email'],'phone':kw['phone']})

                kw['partner_id'] = user_id.partner_id.id
                result['public_user'] = True
        else:
            result['public_user']=False
            

        slate_file=False
        if  kw.get('slate_file',False):
            slate_file=kw.pop('slate_file')

        registry_file=False
        if kw.get('registry_file',False):
            registry_file=kw.pop('registry_file')

        internal_id=internal_slate_obj.sudo().create(kw)

        internal_slate_obj=request.env['internal.slate']
        all_ids=internal_slate_obj.search([('partner_id','=',request.env.user.partner_id.id)])
        list_r = []
        for browse_rec in all_ids:
            list_r.append(browse_rec)
      

        result['internal_slate']=list_r
        
        if registry_file:
            FileStorage = registry_file
            FileData = FileStorage.read()
            file_base64_seven = base64.encodestring(FileData)
            internal_id.write({'registry_file':file_base64_seven})


        if slate_file:
            FileStorage =slate_file
            FileData = FileStorage.read()
            file_base64_seven = base64.encodestring(FileData)
            internal_id.write({'slate_file':file_base64_seven})
            
        result['sale_url'] = internal_id.sale_url
        result['portal_url'] = internal_id.portal_url
        return request.render("Internal_slate.internal_slate_submit_msg", result)
