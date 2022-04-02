# -*- coding: utf-8 -*-
{
    'name': "error404",

    'summary': """""",

    'description': """""",
    'author': "Mutn",
    'website': "www.mutn.tech",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','http_routing','website'],
    'license': 'LGPL-3',
    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/error_pages.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'web.assets_frontend': [
            'error404/static/src/js/error.js',
            'error404/static/src/scss/error.scss',
        ],
    }
}
