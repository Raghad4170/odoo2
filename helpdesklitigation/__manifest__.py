# -*- coding: utf-8 -*-
{
    'name': "helpdesk law",

    'summary': """""",

    'description': """""",
    'sequence': -1,
    'author': "Mutn",
    'website': "www.mutn.tech",
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base', 'litigation', 'helpdesk', 'project', 'portal','website_helpdesk_form','website_helpdesk'],

    # always loaded
    'data': [
        'data/emails.xml',
        'data/stages.xml',
        'views/views.xml',
        'views/portal.xml',
        'views/portal_view.xml',
        'views/portal_ticket.xml',
        'wizards/views.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'helpdesklitigation/static/src/js/custom.js'
        ],
    },
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
