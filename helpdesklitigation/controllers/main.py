# -*- coding: utf-8 -*-
import base64
import json
import pytz

from datetime import datetime
from psycopg2 import IntegrityError
from werkzeug.exceptions import BadRequest
from odoo.exceptions import AccessError, MissingError
from odoo import http, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from odoo.exceptions import ValidationError, UserError
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers import form
import ast
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
import logging
_logger = logging.getLogger(__name__)

class WebsiteForm(form.WebsiteForm):
    
    
    def _handle_website_form(self, model_name, **kwargs):
        types_ids = False
        if request.params.get('types_ids'):
            types_ids = request.params.get('types_ids')
        request.params['types_ids'] = types_ids

        user_obj = request.env['res.users']
        if model_name == 'helpdesk.ticket':
            if request.env.user.has_group('base.group_public'):
                if request.env["res.users"].sudo().search([("login", "=", kwargs['partner_email'])]):
                    raise UserError(('يوجد لدينا مستخدم بنفس بيانات مقدم الطلب، نأمل منكم رفع الطلب بعد تسجيل الدخول.'))
                else:
                    user_id = user_obj.sudo().create({'login':kwargs['partner_email'],'password':kwargs['partner_phone'],'name':kwargs['partner_name'],'groups_id':[]})
                    group_portal = request.env.ref('base.group_portal')
                    group_portal.sudo().write({'users': [(4, user_id.id)]})
                    user_id.partner_id.sudo().write({'email':kwargs['partner_email'],'phone':kwargs['partner_phone']})
                    
                    request.session['public_user']=True
            else:
                request.session['public_user']=False

        model_record = request.env['ir.model'].sudo().search([('model', '=', model_name), ('website_form_access', '=', True)])
        if not model_record:
            return json.dumps({
                'error': _("The form's specified model does not exist")
            })

        try:
            data = self.extract_data(model_record, request.params)
        # If we encounter an issue while extracting data
        except ValidationError as e:
            # I couldn't find a cleaner way to pass data to an exception
            return json.dumps({'error_fields' : e.args[0]})

        try:

            if model_name == 'helpdesk.ticket':

                ticket_dic={}
                ticket_type_id=int(kwargs['ticket_type_id']) 
                team_id=int(kwargs['team_id'])
                ticket_dic['partner_phone']=kwargs['partner_phone']

                ticket_dic['ticket_type_id']=ticket_type_id
                if kwargs.get('types_ids',False):
                    ticket_dic['types_ids']=int(kwargs['types_ids'])
                ticket_dic['team_id']=team_id
                ticket_dic['partner_name']=kwargs['partner_name']
                ticket_dic['partner_email']=kwargs['partner_email']
                ticket_dic['service_standard']=kwargs['service_standard']
                ticket_dic['name']=kwargs['name']
                ticket_dic['description']=kwargs['description']


                id_record= request.env['helpdesk.ticket'].with_user(SUPERUSER_ID).with_context(mail_create_nosubscribe=True).create(ticket_dic).id
                self.insert_attachment(model_record, id_record, data['attachments'])

            else:
                id_record = self.insert_record(request, model_record, data['record'], data['custom'], data.get('meta'))
                logging.info("-----------id_record------%s",id_record)   

                self.insert_attachment(model_record, id_record, data['attachments'])
                # in case of an email, we want to send it immediately instead of waiting
                # for the email queue to process
                if model_name == 'mail.mail':
                    request.env[model_name].sudo().browse(id_record).send()

        # Some fields have additional SQL constraints that we can't check generically
        # Ex: crm.lead.probability which is a float between 0 and 1
        # TODO: How to get the name of the erroneous field ?
        except IntegrityError:
            return json.dumps(False)

        request.session['form_builder_model_model'] = model_record.model
        request.session['form_builder_model'] = model_record.name
        request.session['form_builder_id'] = id_record

        return json.dumps({'id': id_record})
#   return super(WebsiteForm, self)._handle_website_form(model_name, **kwargs)



class WebsiteHelpdesk(http.Controller):
    
    @http.route("/get_service_cost", type='json', auth="public", website=True)
    def get_service_cost(self,ticket_type_id,service_standard):
        ticket_type_obj=request.env['helpdesk.ticket.type']
        ticket_type_data=ticket_type_obj.sudo().browse(int(ticket_type_id))

        if service_standard == 'عادي':
            service_cost = ticket_type_data.normal_time_taken
            service_days = '(' + str(ticket_type_data.normal_time_taken) + ' / يوم) '

        if service_standard == 'مستعجل':
            service_cost = ticket_type_data.urgent_time_taken
            service_days = '(' + str(ticket_type_data.urgent_time_taken) + ' / يوم) '

        if service_standard == 'طارئ':
            service_cost = ticket_type_data.very_urgent_time_taken
            service_days = '(' + str(ticket_type_data.very_urgent_time_taken) + ' / يوم) '

        if service_cost == 0:
            service_days = ''
            
        return service_days

    
    @http.route("/get_ticket_types_ids", type='json', auth="public", website=True)
    def get_ticket_types_ids(self,ticket_type_id):
        ticket_type_list=[]
        types = request.env['ticket.type.types']
        types_ids = types.sudo().search([('ticket_type_id', '=', int(ticket_type_id))])
        for type_rec in types_ids:
            dic={}
            dic['id']=type_rec.id
            dic['name']=type_rec.name
            ticket_type_list.append(dic)

        return ticket_type_list


    @http.route("/get_service_date", type='json', auth="public", website=True)
    def get_service_date(self,ticket_id):
        ticket_obj=request.env['helpdesk.ticket']
        if ticket_id.find('#')!=-1:
            data=ticket_obj.search([('id','=',ticket_id.split('#')[1])])
            if len(data):
                return data.service_date
            else:
                return False  
            
    def get_helpdesk_team_data(self, team, search=None):
        return {'team': team}

    def _get_partner_data(self):
        partner = request.env.user.partner_id
        partner_values = {}
        if partner != request.website.user_id.sudo().partner_id:
            partner_values['name'] = partner.name
            partner_values['email'] = partner.email
            partner_values['phone'] = partner.phone
        return partner_values

    @http.route(['/helpdesk/', '/helpdesk/<model("helpdesk.team"):team>'], type='http', auth="public", website=True, sitemap=True)
    def website_helpdesk_teams(self, team=None, **kwargs):
        ticket_type_obj=request.env['helpdesk.ticket.type']

        search = kwargs.get('search')
        # For breadcrumb index: get all team
        teams = request.env['helpdesk.team'].search(['|', '|', ('use_website_helpdesk_form', '=', True), ('use_website_helpdesk_forum', '=', True), ('use_website_helpdesk_slides', '=', True)], order="id asc")
        if not request.env.user.has_group('helpdesk.group_helpdesk_manager'):
            teams = teams.filtered(lambda team: team.website_published)
        if not teams:
            return request.render("website_helpdesk.not_published_any_team")
        result = self.get_helpdesk_team_data(team or teams[0], search=search)
        # For breadcrumb index: get all team
        ticket_types=ticket_type_obj.sudo().search([])
        
        result['ticket_types_list'] = ticket_types
        result['standard_list'] = ['عادي','مستعجل','طارئ']
        result['teams'] = teams
        result['default_partner_values'] = self._get_partner_data()

        return request.render("website_helpdesk.team", result)
    
    
class CustomerPortal(CustomerPortal):
    
    @http.route([
        "/helpdesk/ticket/<int:ticket_id>",
        "/helpdesk/ticket/<int:ticket_id>/<access_token>",
        '/my/ticket/<int:ticket_id>',
        '/my/ticket/<int:ticket_id>/<access_token>'
    ], type='http', auth="public", website=True)
    def tickets_followup(self, ticket_id=None, access_token=None, **kw):
        try:
            ticket_sudo = self._document_check_access('helpdesk.ticket', ticket_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._ticket_get_page_view_values(ticket_sudo, access_token, **kw)
        return request.render("helpdesklitigation.tickets_followups", values)
    

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        if values.get('sales_user', False):
            values['title'] = _("Salesperson")
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'ticket_count' in counters:
            values['ticket_count'] = (
                request.env['helpdesk.ticket'].search_count([])
                if request.env['helpdesk.ticket'].check_access_rights('read', raise_exception=False)
                else 0
            )
        return values

    def _ticket_get_page_view_values(self, ticket, access_token, **kwargs):
        values = {
            'page_name': 'ticket',
            'ticket': ticket,
        }
        return self._get_page_view_values(ticket, access_token, values, 'my_tickets_history', False, **kwargs)

    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'], type='http', auth="user", website=True)
    def my_helpdesk_tickets(self, page=1, date_begin=None, date_end=None, sortby=None, filterby='open', search=None, groupby='none', search_in='content', **kw):
        values = self._prepare_portal_layout_values()

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Subject'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
            'reference': {'label': _('Reference'), 'order': 'id'},
            'update': {'label': _('Last Stage Update'), 'order': 'date_last_stage_update desc'},
        }
        searchbar_filters = {
            'open': {'label': _('قيد التنفيذ'), 'domain': [('stage_id.un_seen', '=', False)]},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
            'id': {'input': 'id', 'label': _('Search in Reference')},
            'status': {'input': 'status', 'label': _('Search in Stage')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'stage': {'input': 'stage_id', 'label': _('Stage')},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if filterby in ['last_message_sup', 'last_message_cust']:
            discussion_subtype_id = request.env.ref('mail.mt_comment').id
            messages = request.env['mail.message'].search_read([('model', '=', 'helpdesk.ticket'), ('subtype_id', '=', discussion_subtype_id)], fields=['res_id', 'author_id'], order='date desc')
            last_author_dict = {}
            for message in messages:
                if message['res_id'] not in last_author_dict:
                    last_author_dict[message['res_id']] = message['author_id'][0]

            ticket_author_list = request.env['helpdesk.ticket'].search_read(fields=['id', 'partner_id'])
            ticket_author_dict = dict([(ticket_author['id'], ticket_author['partner_id'][0] if ticket_author['partner_id'] else False) for ticket_author in ticket_author_list])

            last_message_cust = []
            last_message_sup = []
            for ticket_id in last_author_dict.keys():
                if last_author_dict[ticket_id] == ticket_author_dict[ticket_id]:
                    last_message_cust.append(ticket_id)
                else:
                    last_message_sup.append(ticket_id)

            if filterby == 'last_message_cust':
                domain = [('id', 'in', last_message_cust)]
            else:
                domain = [('id', 'in', last_message_sup)]

        else:
            domain = searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                discussion_subtype_id = request.env.ref('mail.mt_comment').id
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search), ('message_ids.subtype_id', '=', discussion_subtype_id)]])
            if search_in in ('status', 'all'):
                search_domain = OR([search_domain, [('stage_id', 'ilike', search)]])
            domain += search_domain

        # pager
        tickets_count = len(request.env['helpdesk.ticket'].search(domain))
        pager = portal_pager(
            url="/my/tickets",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'search_in': search_in, 'search': search, 'groupby': groupby},
            total=tickets_count,
            page=page,
            step=self._items_per_page
        )

        tickets = request.env['helpdesk.ticket'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_tickets_history'] = tickets.ids[:100]

        if groupby == 'stage':
            grouped_tickets = [request.env['helpdesk.ticket'].concat(*g) for k, g in groupbyelem(tickets, itemgetter('stage_id'))]
        else:
            grouped_tickets = [tickets]
            
        values.update({
            'date': date_begin,
            'grouped_tickets': grouped_tickets,
            'page_name': 'ticket',
            'default_url': '/my/tickets',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': searchbar_filters,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'search_in': search_in,
            'search': search,
            'filterby': filterby,
        })
        return request.render("helpdesk.portal_helpdesk_ticket", values)
