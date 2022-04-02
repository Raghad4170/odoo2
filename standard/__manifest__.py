# -*- coding: utf-8 -*-
{
    'name': "النماذج الموحدة",
    'summary': """النماذج الموحدة""",
    'author': "Mutn",
    'website': "www.mutn.tech",
    'license': 'LGPL-3',
    'sequence': -111,
    # for the full list
    'category': 'Mutn',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','portal','parentid'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/portal.xml',
        'views/report.xml',
        'views/contract.xml',
    ],
    'application': True,
    'assets': {'web.assets_frontend': ['standard/static/src/js/sign.js',]}
}
