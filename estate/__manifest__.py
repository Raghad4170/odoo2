# -*- coding: utf-8 -*-
{
    'name': "Customer Estate Management",

    'summary': """Customer Estate Management""",

    'description': """""",
    'sequence': 3,
    'author': "Mutn",
    'website': "www.mutn.tech",
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base', 'portal', 'utm', 'website'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/portal.xml',
        'views/cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False

}
