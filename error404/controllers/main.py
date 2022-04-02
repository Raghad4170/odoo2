import base64
import json

from odoo import http, SUPERUSER_ID, _
from odoo.http import request
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
import dateutil
from dateutil.relativedelta import relativedelta

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import logging
_logger = logging.getLogger(__name__)

class exceptions(http.Controller):

    
    @http.route(['/submit_err_msg'], type='json', auth="public", csrf=False,website=True)
    def submit_err_msg(self,kw):
        error_obj =request.env['error404.error404']
        error_obj.sudo().create({'name':kw['status_name'],'description':kw['status_message']})

        return True
