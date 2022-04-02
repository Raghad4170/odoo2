# -*- coding: utf-8 -*-
{
    'name': "User Log Details",
    'version': '15.0.1.0.0',
    'summary': """Timeout, Session, Session Timeout, Session Termination""",
    'description': """This module records login information of user""",
    'author': "Mutn",
    'website': "www.mutn.tech",
    'category': 'Tools',
    'depends': ['base'],
    'license': 'AGPL-3',
    'post_init_hook' : 'post_init_hook',
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/ir_cron.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
