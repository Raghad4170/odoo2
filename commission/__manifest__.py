# -*- coding: utf-8 -*-
{
    'name': "commission",

    'summary': """""",

    'description': """""",
    'sequence': 4,
    'author': "Mutn",
    'website': "www.mutn.tech",
    'category': 'Human Resources/Attendances',
    'version': '0.1',
    'license': 'LGPL-3',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sign'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
