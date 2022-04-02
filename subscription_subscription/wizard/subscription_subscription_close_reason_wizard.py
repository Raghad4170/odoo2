# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleSubscriptionCloseReasonWizard(models.TransientModel):
    _name = "subscription.subscription.close.reason.wizard"
    _description = 'Subscription Close Reason Wizard'

    close_reason_id = fields.Many2one("subscription.subscription.close.reason", string="Close Reason")

    def set_close(self):
        self.ensure_one()
        subscription = self.env['subscription.subscription'].browse(self.env.context.get('active_id'))
        subscription.close_reason_id = self.close_reason_id
        subscription.set_close()
