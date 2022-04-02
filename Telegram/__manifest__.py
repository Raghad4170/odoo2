# -*- coding: utf-8 -*-
{
    'name': "Telegram",

    'summary': """""",

    'description': """""",

    'author': "Mutn",
    'website': "www.mutn.tech",
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base','mail','litigation','account','hr_attendance','helpdesklitigation','balagh','Internal_slate','debt','login_user_detail','parentid','hr_payroll','Bills','avatar'],
    # always loaded
    'data': [
        'views/views.xml',
        'views/cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
