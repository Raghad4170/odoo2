from odoo import models, fields, api
import odoo
from datetime import timedelta
import socket
import os
import time
from odoo.tools import config

class Session(models.Model):
    _name = 'ir.session'
    _description = 'Session'
    _log_access = False
    
    name = fields.Char(required = True, string='Session ID')
    user_id = fields.Many2one('res.users', required = True)
    start_date = fields.Datetime()
    last_request_time = fields.Datetime()
    remote_addr = fields.Char()
    user_agent = fields.Char()
    hostname = fields.Char()
    
    _sql_constraints = [
        ('uk_name', 'unique(name)', 'Session ID should be unique!'),
        ]    
    
    @api.model
    def update_session(self, session, httprequest):
        now = fields.Datetime.now()
        hostname = socket.gethostname()
        cr = self.env.cr
        cr.execute("update ir_session set last_request_time=%s, user_id=%s, hostname=%s where name=%s", [now, session.uid, hostname, session.sid])
        if cr.rowcount:
            return        
        vals = {
            'last_request_time' : now,
            'user_agent' : httprequest.user_agent,
            'name' : session.sid,
            'start_date' : now,
            'user_id' : session.uid,
            'hostname' : hostname         
            }
        if config['proxy_mode'] and httprequest.headers.get('X-Forwarded-For'):
            vals['remote_addr'] = httprequest.headers.get('X-Forwarded-For').split(",")[0]
        else:
            vals['remote_addr'] = httprequest.remote_addr
            
        self.create(vals)                      
        self.env['session.session'].create(vals)

    def unlink(self):
        session_store = odoo.http.root.session_store
        for record in self:
            session = session_store.get(record.name)
            session_store.delete(session)
            all_session = self.env['session.session'].search([('name', '=', record.name)])
            for session in all_session:
                session.end_date = fields.Datetime.now()
        return super(Session, self).unlink()
    
    @api.model
    def _session_gc(self):
        session_timeout = float(self.env['ir.config_parameter'].get_param('session_timeout', 60))
        dt = fields.Datetime.now() - timedelta(minutes = session_timeout)
        sessions = self.env['ir.session'].search([('last_request_time', '<', dt)])
        for thesession in sessions:
            name = thesession.name
            all_session = self.env['session.session'].search([('name', '=', name)])
            for session in all_session:
                session.end_date = fields.Datetime.now()
            thesession.unlink() 
                
                
                
class Sessions(models.Model):
    _name = 'session.session'
    _description = 'Sessions'
    
    name = fields.Char(string='Session ID')
    user_id = fields.Many2one('res.users', required = True)
    start_date = fields.Datetime()
    end_date = fields.Datetime()
    last_request_time = fields.Datetime()
    remote_addr = fields.Char()
    user_agent = fields.Char()
    hostname = fields.Char()

