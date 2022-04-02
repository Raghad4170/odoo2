# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _message_auto_subscribe_notify(self, partner_ids, template):
        """ Notify new followers, using a template to render the content of the
        notification message. Notifications pushed are done using the standard
        notification mechanism in mail.thread. It is either inbox either email
        depending on the partner state: no user (email, customer), share user
        (email, customer) or classic user (notification_type)

        :param partner_ids: IDs of partner to notify;
        :param template: XML ID of template used for the notification;
        """
        if not self or self.env.context.get('mail_auto_subscribe_no_notify'):
            return
        if not self.env.registry.ready:  # Don't send notification during install
            return

        view = self.env['ir.ui.view'].browse(self.env['ir.model.data']._xmlid_to_res_id(template))

        for record in self:
            model_description = self.env['ir.model']._get(record._name).display_name
            values = {
                'object': record,
                'model_description': model_description,
                'access_link': record._notify_get_action_link('view'),
            }
            assignation_msg = view._render(values, engine='ir.qweb', minimal_qcontext=True)
            assignation_msg = self.env['mail.render.mixin']._replace_local_links(assignation_msg)

class Teams(models.Model):
    _inherit = "crm.team"
    
    partnerـrate = fields.Float(string='نسبة الفريق')
    is_company_partner = fields.Boolean("شريك للشركة")

class AccountMove(models.Model):
    _inherit = "account.move"

    
    invoice_commission_type = fields.Selection([
        ('with', 'بعمولة'),
        ('without', 'بدون عمولة'),
        ], string='نوع العمولة')
    partner_entry_type = fields.Selection([
        ('partner_income', 'إيراد شريك'),
        ('partner_income_company', 'إيراد شريك مشترك مع الشركة'),
        ('partner_expense', 'مصروف شريك'),
        ('partner_expense_company', 'مصروف شريك تتحمله الشركة'),
        ], string='نوع قيد الشريك', store=True)
    is_company_partner = fields.Boolean(related='team_id.is_company_partner')
    team_leader = fields.Many2one('res.users', related='team_id.user_id', store=True)
    
    is_partner_move = fields.Boolean(compute='_is_partner_move', store=True)
    
    @api.depends('partner_entry_type', 'is_company_partner', 'team_id', 'partner_commission', 'price_subtotal_exp', 'team_id.is_company_partner')
    def _is_partner_move(self):
        for move in self:
            is_partner_move = False
            if move.move_type == 'entry':
                if move.partner_entry_type:
                    is_partner_move = True
            else:
                if move.is_company_partner:
                    is_partner_move = True
            move.is_partner_move = is_partner_move
    

    commissionـrate = fields.Float(string='نسبة العمولة')
    commission_total = fields.Float(string='العمولة', compute='_compute_commission', store=True)
    company_commission_total = fields.Float(string='عمولة الشركة', compute='_compute_commission', store=True)
    partner_commission = fields.Float(string='عمولة الشريك', compute='_compute_commission', store=True)
    partner_commission_claimed = fields.Float(string='عمولة الشريك على اساس نقدي', compute='_compute_commission', store=True)
    partner_commission_not_claimed = fields.Float(string='عمولة الشريك على اساس استحقاق', compute='_compute_commission', store=True)
    company_commission_total_claimed = fields.Float(string='عمولة الشركة على اساس نقدي', compute='_compute_commission', store=True)
    company_commission_total_not_claimed = fields.Float(string='عمولة الشركة على اساس استحقاق', compute='_compute_commission', store=True)
    
    @api.depends('amount_untaxed_signed', 'commissionـrate', 'team_id.partnerـrate', 'team_id', 'commission_total', 'invoice_commission_type', 'move_type', 'partner_entry_type','is_partner_move')
    def _compute_commission(self):
        for move in self:
            commission_total = 0.0
            after_commission_total = 0.0
            partner_commission = 0.0
            partner_commission_claimed = 0.0
            partner_commission_not_claimed = 0.0
            company_commission_total_claimed = 0.0
            company_commission_total_not_claimed = 0.0
            if move.move_type == 'out_invoice' or move.partner_entry_type == 'partner_income_company':
                after_commission_total = move.amount_untaxed_signed
                if move.commissionـrate:
                    commission_total = move.amount_untaxed_signed * (move.commissionـrate / 100)
                    after_commission_total = move.amount_untaxed_signed - commission_total
                if move.team_id.partnerـrate:
                    partner_commission = after_commission_total * (move.team_id.partnerـrate / 100)
            elif move.partner_entry_type == 'partner_income':
                partner_commission = (move.amount_total_signed / len(move.line_ids))
            move.commission_total = commission_total
            move.company_commission_total = after_commission_total - partner_commission
            move.partner_commission = partner_commission
            
            if move.payment_state == 'paid':
                partner_commission_claimed = partner_commission
                company_commission_total_claimed = after_commission_total - partner_commission
            else:
                partner_commission_not_claimed = partner_commission
                company_commission_total_not_claimed = after_commission_total - partner_commission
            
            move.partner_commission_claimed = partner_commission_claimed
            move.company_commission_total_claimed = company_commission_total_claimed
            move.partner_commission_not_claimed = partner_commission_not_claimed
            move.company_commission_total_not_claimed = company_commission_total_not_claimed
            
    price_subtotal_exp = fields.Float(string='مصروفات الشريك', compute='_compute_price_subtotal_exp', store=True)
    price_subtotal_company_exp = fields.Float(string='مصروفات الشركة', compute='_compute_price_subtotal_exp', store=True)

    @api.depends('move_type', 'amount_untaxed_signed', 'partner_entry_type')
    def _compute_price_subtotal_exp(self):
        for move in self:
            price_subtotal_exp = 0.0
            price_subtotal_company_exp = 0.0
            if move.move_type == 'in_invoice':
                price_subtotal_exp = move.amount_untaxed_signed
            elif move.partner_entry_type == 'partner_expense':
                price_subtotal_exp = - (move.amount_total_signed / len(move.line_ids))
            elif move.partner_entry_type == 'partner_expense_company':
                price_subtotal_company_exp = - (move.amount_total_signed / len(move.line_ids))
            move.price_subtotal_exp = price_subtotal_exp
            move.price_subtotal_company_exp = price_subtotal_company_exp


class AccountInvoiceReport(models.Model):
    _name = "account.invoice.report.partner"
    _description = "تقارير الشركاء"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    move_id = fields.Many2one('account.move', readonly=True)
    journal_id = fields.Many2one('account.journal', string='دفتر اليومية', readonly=True)
    company_id = fields.Many2one('res.company', string='الشركة', readonly=True)
    company_currency_id = fields.Many2one('res.currency', string='العملة', readonly=True)
    partner_id = fields.Many2one('res.partner', string='العميل', readonly=True)
    commercial_partner_id = fields.Many2one('res.partner', string='شركة العميل')
    country_id = fields.Many2one('res.country', string="الدولة")
    invoice_user_id = fields.Many2one('res.users', string='الشريك', readonly=True, store=True)
    move_type = fields.Selection([
        ('entry', 'قيد'),
        ('out_invoice', 'فاتورة عميل'),
        ('in_invoice', 'فاتورة مورد'),
        ], string='نوع الفاتورة', readonly=True)
    is_partner_move = fields.Boolean(compute='_is_partner_move', store=True, readonly=True)
    state = fields.Selection([
        ('draft', 'مسودة'),
        ('posted', 'مرحل'),
        ('cancel', 'ملغي')
        ], string='حالة الفاتورة', readonly=True)
    payment_state = fields.Selection(selection=[
        ('not_paid', 'غير مسدد'),
        ('in_payment', 'في دفعة'),
        ('paid', 'مدفوع'),
        ('partial', 'مسدد جزئياً'),
    ], string='حالة الدفعة', readonly=True)
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='الموقف المالي', readonly=True)
    date = fields.Date(readonly=True, string="تاريخ الفاتورة")
    product_id = fields.Many2one('product.product', string='المنتج', readonly=True)
    product_uom_id = fields.Many2one('uom.uom', string='وحدة القياس', readonly=True)
    product_categ_id = fields.Many2one('product.category', string='فئة المنتج', readonly=True)
    invoice_date_due = fields.Date(string='تاريخ الاستحقاق', readonly=True)
    account_id = fields.Many2one('account.account', string='حساب الإيرادات / المصاريف', readonly=True, domain=[('deprecated', '=', False)])
    analytic_account_id = fields.Many2one('account.analytic.account', string='حساب تحليلي', groups="analytic.group_analytic_accounting")
#     price_subtotal = fields.Float(string='صافي الربح/الخسارة', readonly=True)
    partner_commission = fields.Float(string='إيرادات الشريك', readonly=True)
    company_commission_total = fields.Float(string='إيرادات الشركة', readonly=True)
    price_subtotal_exp = fields.Float(string='مصروفات الشريك', readonly=True)
    price_subtotal_company_exp = fields.Float(string='مصروفات الشركة', readonly=True)

    partner_commission_claimed = fields.Float(string='عمولة الشريك على اساس نقدي', readonly=True)
    partner_commission_not_claimed = fields.Float(string='عمولة الشريك على اساس استحقاق', readonly=True)
    company_commission_total_claimed = fields.Float(string='عمولة الشركة على اساس نقدي', readonly=True)
    company_commission_total_not_claimed = fields.Float(string='عمولة الشركة على اساس استحقاق', readonly=True)
    team_id = fields.Many2one('crm.team', string='فريق العلاقات', readonly=True)
    team_leader = fields.Many2one('res.users', string='قائد الفريق', readonly=True, store=True)

    _depends = {
        'account.move': [
            'name', 'state', 'move_type', 'is_partner_move', 'partner_id', 'invoice_user_id', 'team_id', 'team_leader', 'fiscal_position_id', 'partner_commission',
            'date', 'invoice_date_due', 'invoice_payment_term_id', 'partner_bank_id', 'price_subtotal_exp', 'price_subtotal_company_exp', 'company_commission_total',
            'partner_commission_claimed', 'partner_commission_not_claimed', 'company_commission_total_claimed', 'company_commission_total_not_claimed',
        ],
        'account.move.line': [
            'amount_residual', 'balance', 'amount_currency',
            'move_id', 'product_id', 'product_uom_id', 'account_id', 'analytic_account_id',
            'journal_id', 'company_id', 'currency_id', 'partner_id',
        ],
        'product.product': ['product_tmpl_id'],
        'product.template': ['categ_id'],
        'uom.uom': ['category_id', 'factor', 'name', 'uom_type'],
        'res.currency.rate': ['currency_id', 'name'],
        'res.partner': ['country_id'],
    }

    @property
    def _table_query(self):
        return '%s %s %s' % (self._select(), self._from(), self._where())

    @api.model
    def _select(self):
        return '''
            SELECT
                line.id,
                line.move_id,
                line.product_id,
                line.account_id,
                line.analytic_account_id,
                line.journal_id,
                line.company_id,
                line.company_currency_id,
                line.partner_id AS commercial_partner_id,
                move.state,
                move.move_type,
                move.is_partner_move,
                move.partner_id,
                move.invoice_user_id,
                move.team_id,
                move.team_leader,
                move.fiscal_position_id,
                move.price_subtotal_exp,
                move.price_subtotal_company_exp,
                move.company_commission_total,
                move.partner_commission,
                move.partner_commission_claimed,
                move.partner_commission_not_claimed,
                move.company_commission_total_claimed,
                move.company_commission_total_not_claimed,
                move.payment_state,
                move.date,
                move.invoice_date_due,
                uom_template.id                                             AS product_uom_id,
                template.categ_id                                           AS product_categ_id,
                COALESCE(partner.country_id, commercial_partner.country_id) AS country_id
        '''

    @api.model
    def _from(self):
        return '''
            FROM account_move_line line
                LEFT JOIN res_partner partner ON partner.id = line.partner_id
                LEFT JOIN product_product product ON product.id = line.product_id
                LEFT JOIN account_account account ON account.id = line.account_id
                LEFT JOIN account_account_type user_type ON user_type.id = account.user_type_id
                LEFT JOIN product_template template ON template.id = product.product_tmpl_id
                LEFT JOIN uom_uom uom_line ON uom_line.id = line.product_uom_id
                LEFT JOIN uom_uom uom_template ON uom_template.id = template.uom_id
                INNER JOIN account_move move ON move.id = line.move_id
                LEFT JOIN res_partner commercial_partner ON commercial_partner.id = move.commercial_partner_id
                JOIN {currency_table} ON currency_table.company_id = line.company_id
        '''.format(
            currency_table=self.env['res.currency']._get_query_currency_table({'multi_company': True, 'date': {'date_to': fields.Date.today()}}),
        )

    @api.model
    def _where(self):
        return '''
            WHERE move.move_type IN ('out_invoice', 'in_invoice', 'out_receipt', 'in_receipt', 'entry')
                AND move.state IN ('draft', 'posted')
                AND move.is_partner_move IS True
                AND line.account_id IS NOT NULL
                AND NOT line.exclude_from_invoice_tab
        '''


