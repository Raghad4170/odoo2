# -*- coding: utf-8 -*-
{
    'name': "hideodoo",

    'summary': """Hiding odoo from website""",

    'description': """""",

    'author': "Mutn",
    'website': "www.mutn.tech",
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base','portal','mail','parentid'],

    # always loaded
    'data': [
        'views.xml',
        'email.xml',
    ],
}
