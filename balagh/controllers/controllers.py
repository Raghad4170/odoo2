# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import Website
from datetime import datetime, timedelta, date

# Form
class Balagh(http.Controller):
    
    @http.route(['/submit_balag_msg'], type='json', auth="public", csrf=False,website=True)
    def submit_balag_msg(self,kw):
        balagh_sub_obj = request.env['balagh.balagh']
        users_obj = request.env['res.users']
        balagh_message_obj = request.env['balagh.messages']

        if request.env.user.has_group('base.group_public'):
            if request.env["res.users"].sudo().search([("login", "=", kw['email'])]):
                raise AccessError(('يوجد لدينا مستخدم بنفس بيانات مقدم الطلب، نأمل منكم رفع الطلب بعد تسجيل الدخول.'))
            else:
                user_id=users_obj.sudo().create({'login':kw['email'],'password':kw['phone'],'name':kw['sender_name'],'groups_id':[]})
                group_portal = request.env.ref('base.group_portal')
                group_portal.sudo().write({'users': [(4, user_id.id)]})
                group_balagh_user = request.env.ref('balagh.group_balagh_user')
                group_balagh_user.sudo().write({'users': [(4, user_id.id)]})
                user_id.partner_id.sudo().write({'email':kw['email'],'phone':kw['phone']})
                partner_id = user_id.partner_id.id
        else:
            partner_id = request.env.user.partner_id.id

        balagh_sub_obj.sudo().create({'partner_id':partner_id,
                                      'recever_id':kw['recever_id'],
                                      'recever_name':kw['recever_name'],
                                      'sender_name':kw['sender_name'],
                                      'balagh_id':int(kw['msg_id']),
                                      'variable_1':kw['m1'] if kw.get('m1',False) else None,
                                      'variable_2':kw['m2'] if kw.get('m2',False) else None,
                                      'variable_3':kw['m3'] if kw.get('m3',False) else None,
                                      'variable_4':kw['m4'] if kw.get('m4',False) else None,
                                      'variable_5':kw['m5'] if kw.get('m5',False) else None,
                                      'variable_6':kw['m6'] if kw.get('m6',False) else None,
                                      'variable_7':kw['m7'] if kw.get('m7',False) else None,
                                      'variable_8':kw['m8'] if kw.get('m8',False) else None})
        return True
    
    
    
    @http.route(['/balagh_sucsess'], type='http', auth="public", website=True)
    def balagh_sucsess(self,**kw):
        result={}
        if request.env.user.has_group('base.group_public'):
            result['public_user'] = True
        else:
            result['public_user']=False
        return request.render("balagh.balagh_sucsess", result)

    
    
    
    @http.route(['/new/balagh/<int:msg_id>'], type='http', auth="public", website=True)
    def new_balagh_form(self,msg_id=0,**kw):
        balagh_message_obj=request.env['balagh.messages']
        user_obj=request.env['res.users']
        msg=balagh_message_obj.sudo().browse(msg_id)
        if request.env.user.has_group('base.group_public'):
            public_user = True
            name=''
        else:
            public_user = False
            name=request.env.user.partner_id.name

        return request.render("balagh.new_balagh_form", {'msg':msg,'sender_name':name,'public_user':public_user})


    @http.route(['/new/balagh'], type='http', auth="public", website=True)
    def new_balagh(self,**kw):
        balagh_message_obj=request.env['balagh.messages']
        msg_id=balagh_message_obj.sudo().search([])
        msg_list=[]
        msg_dic={}
        for msg in msg_id:
            msg_dic['name']=msg.name
            msg_dic['message']=msg.message
            msg_dic['variables']=msg.variables
            msg_dic['id']=int(msg.id)
            msg_list.append(msg_dic)
            msg_dic={}
        return request.render("balagh.new_balagh", {'balagh_msg_list':msg_list})

class CustomerPortal(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'balagh_count' in counters:
            values['balagh_count'] = request.env['balagh.balagh'].search_count([])
        return values
 
    # ------------------------------------------------------------
    # My balagh
    # ------------------------------------------------------------
    def _balagh_get_page_view_values(self, balagh, access_token, **kwargs):
        values = {
            'page_name': 'بلاغ',
            'balagh': balagh,
        }
        return self._get_page_view_values(balagh, access_token, values, 'my_balaghs_history', False, **kwargs)

    @http.route(['/my/balaghs', '/my/balaghs/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_balaghs(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        balagh = request.env['balagh.balagh']
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
            
        # building count
        balagh_count = balagh.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/balaghs",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=balagh_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        balaghs = balagh.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_balaghs_history'] = balaghs.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'balaghs': balaghs,
            'page_name': 'balagh',
            'default_url': '/my/balaghs',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("balagh.portal_my_balaghs", values)

    @http.route(['/my/balagh/<int:balagh_id>'], type='http', auth="public", website=True)
    def portal_my_balagh(self, balagh_id=None, access_token=None, **kw):
        try:
            balagh_sudo = self._document_check_access('balagh.balagh', balagh_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._balagh_get_page_view_values(balagh_sudo, access_token, **kw)
        return request.render("balagh.portal_my_balagh", values)


