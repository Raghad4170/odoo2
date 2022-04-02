# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
from operator import itemgetter

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem

from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'building_count' in counters:
            values['building_count'] = request.env['building.building'].search_count([])
        if 'contract_count' in counters:
            values['contract_count'] = request.env['contract.contract'].search_count([])
        if 'contracts_count' in counters:
            values['contracts_count'] = request.env['contract.contract'].search_count([])
        if 'unit_count' in counters:
            values['unit_count'] = request.env['unit.unit'].search_count([])
        return values
    
    # ------------------------------------------------------------
    # My building
    # ------------------------------------------------------------
    def _building_get_page_view_values(self, building, access_token, **kwargs):
        values = {
            'page_name': 'building',
            'building': building,
        }
        return self._get_page_view_values(building, access_token, values, 'my_buildings_history', False, **kwargs)

    @http.route(['/my/buildings', '/my/buildings/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_buildings(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        building = request.env['building.building']
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
        building_count = building.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/buildings",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=building_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        buildings = building.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_buildings_history'] = buildings.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'buildings': buildings,
            'page_name': 'building',
            'default_url': '/my/buildings',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("estate.portal_my_buildings", values)

    
    @http.route(['/my/building/<int:building_id>'], type='http', auth="public", website=True)
    def portal_my_building(self, building_id=None, access_token=None, **kw):
        try:
            building_sudo = self._document_check_access('building.building', building_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._building_get_page_view_values(building_sudo, access_token, **kw)
        return request.render("estate.portal_my_building", values)
    
    
    # ------------------------------------------------------------
    # My unit
    # ------------------------------------------------------------
    def _unit_get_page_view_values(self, unit, access_token, **kwargs):
        values = {
            'page_name': 'unit',
            'unit': unit,
        }
        return self._get_page_view_values(unit, access_token, values, 'my_units_history', False, **kwargs)

    @http.route(['/my/units', '/my/units/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_units(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        unit = request.env['unit.unit']
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'building': {'input': 'building', 'label': _('Building')},
        }
        
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
            
        # extends filterby criteria with building the customer has access to
        buildings = request.env['building.building'].search([])
        for building in buildings:
            searchbar_filters.update({
                str(building.id): {'label': building.name, 'domain': [('building_id', '=', building.id)]}
            })

        # extends filterby criteria with building (criteria name is the building id)
        # Note: portal users can't view building they don't follow
        building_groups = request.env['unit.unit'].read_group([('building_id', 'not in', building.ids)],
                                                                ['building_id'], ['building_id'])
        for group in building_groups:
            building_id = group['building_id'][0] if group['building_id'] else False
            building_name = group['building_id'][1] if group['building_id'] else _('Others')
            searchbar_filters.update({
                str(building_id): {'label': building_name, 'domain': [('building_id', '=', building_id)]}
            })
            
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']

        # default group by value
        if not groupby:
            groupby = 'building'

        # unit count
        unit_count = unit.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/units",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=unit_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        if groupby == 'building':
            order = "building_id, %s" % order  # force sort on building first to group by building in view
        units = unit.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_units_history'] = units.ids[:100]

        if groupby == 'building':
            grouped_units = [request.env['unit.unit'].concat(*g) for k, g in groupbyelem(units, itemgetter('building_id'))]
        

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_units': grouped_units,
            'units': units,
            'page_name': 'unit',
            'default_url': '/my/units',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'filterby': filterby,
            'groupby': groupby,
            'sortby': sortby
        })
        return request.render("estate.portal_my_units", values)


    # ------------------------------------------------------------
    # My contract
    # ------------------------------------------------------------
    def _contract_get_page_view_values(self, contract, access_token, **kwargs):
        values = {
            'page_name': 'contract',
            'contract': contract,
        }
        return self._get_page_view_values(contract, access_token, values, 'my_contracts_history', False, **kwargs)

    @http.route(['/my/estatecontracts', '/my/estatecontracts/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_contracts(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        contract = request.env['contract.contract']
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        

        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
            
        # extends filterby criteria with unit the customer has access to
        units = request.env['unit.unit'].search([])
        for unit in units:
            searchbar_filters.update({
                str(unit.id): {'label': unit.name, 'domain': [('unit_id', '=', unit.id)]}
            })
            
        buildings = request.env['building.building'].search([])
        for building in buildings:
            searchbar_filters.update({
                str(building.id): {'label': building.name, 'domain': [('building_id', '=', building.id)]}
            })

        # extends filterby criteria with unit (criteria name is the unit id)
        # Note: portal users can't view unit they don't follow
        unit_groups = request.env['contract.contract'].read_group([('unit_id', 'not in', unit.ids)],
                                                                ['unit_id'], ['unit_id'])
        for group in unit_groups:
            unit_id = group['unit_id'][0] if group['unit_id'] else False
            unit_name = group['unit_id'][1] if group['unit_id'] else _('Others')
            searchbar_filters.update({
                str(unit_id): {'label': unit_name, 'domain': [('unit_id', '=', unit_id)]}
            })

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
        

        # contract count
        contract_count = contract.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/estatecontracts",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=contract_count,
            page=page,
            step=self._items_per_page
        )

        contracts = contract.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_contracts_history'] = contracts.ids[:100]
        

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'contracts': contracts,
            'page_name': 'contract',
            'default_url': '/my/estatecontracts',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'filterby': filterby,
            'sortby': sortby
        })
        return request.render("estate.portal_my_contracts", values)

    @http.route(['/my/estatecontract/<int:contract_id>'], type='http', auth="public", website=True)
    def portal_my_contract(self, contract_id=None, access_token=None, **kw):
        try:
            contract_sudo = self._document_check_access('contract.contract', contract_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._contract_get_page_view_values(contract_sudo, access_token, **kw)
        return request.render("estate.portal_my_contract", values)

    
