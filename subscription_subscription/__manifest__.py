# -*- coding: utf-8 -*-

{
    'name': 'Subscriptions',
    'version': '1.1',
    'category': 'Sales/Subscriptions',
    'sequence': 115,
    'summary': 'Generate recurring invoices and manage renewals',
    'description': """
This module allows you to manage subscriptions.

Features:
    - Create & edit subscriptions
    - Modify subscriptions with sales orders
    - Generate invoice automatically at fixed intervals
""",
    'author': 'Mutn',
    'website': 'www.mutn.tech',
    'depends': [
        'sale_management',
        'portal',
        'web_cohort',
        'rating',
        'base_automation',
        'sms',
    ],
    'data': [
        'security/subscription_subscription_security.xml',
        'security/ir.model.access.csv',
        'security/sms_security.xml',
        'wizard/subscription_subscription_close_reason_wizard_views.xml',
        'wizard/subscription_subscription_wizard_views.xml',
        'wizard/subscription_subscription_renew_wizard_views.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
        'views/res_partner_views.xml',
        'views/subscription_subscription_views.xml',
        'views/account_analytic_account_views.xml',
        'views/subscription_portal_templates.xml',
        'views/mail_activity_views.xml',
        'data/mail_template_data.xml',
        'data/subscription_subscription_data.xml',
        'data/sms_template_data.xml',
        'report/subscription_subscription_report_view.xml',
    ],
    'application': True,
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'subscription_subscription/static/src/js/tours/subscription_subscription.js',
            'subscription_subscription/static/src/scss/subscription_subscription_backend.scss',
        ],
        'web.assets_frontend': [
            'subscription_subscription/static/src/js/portal_subscription.js',
        ],
    }
}
