from odoo import http
import odoo
from odoo.tools import config
from contextlib import closing

original_setup_session = http.Root.setup_session
import logging

_logger = logging.getLogger(__name__)

def setup_session(self, httprequest):
    res = original_setup_session(self, httprequest)
    try:
        session = httprequest.session
        if session.db and session.uid and not httprequest.path.startswith('/longpolling') and config.get("update_session_enabled", True):
            with closing(odoo.registry(session.db).cursor() ) as cr:            
                cr._cnx.autocommit = True   
                env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
                if 'ir.session' in env:
                    env['ir.session'].update_session(session, httprequest)
                cr.commit()                
                
    except Exception as e:
        _logger.exception(e)
        
    return res

http.Root.setup_session = setup_session
