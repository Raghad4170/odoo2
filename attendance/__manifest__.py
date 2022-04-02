# -*- coding: utf-8 -*-
# Copyright to Mutn
{
    'name': 'Late detections',
    'version': '2.0',
    'category': 'Human Resources/Attendances',
    'sequence': 1,
    'summary': 'Track employee attendance ',
    'description': """""",
    'author': "Mutn",
    'website': "www.mutn.tech",
    'license': 'LGPL-3',
    'depends': ['hr_attendance','hr_payroll','hr_holidays','hr_contract','hr_work_entry','hr_work_entry_contract_enterprise','work_trip'],
    'data': [
        'data/cron.xml',
        'data/mail_template.xml',
        'views/correcting.xml',
        'views/views.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'attendance/static/src/js/late.js',
            'attendance/static/src/js/show_button.js'
        ],
        'web.assets_qweb': [
            'attendance/static/src/xml/spe_button.xml'
        ],
    },
    'installable': True,
    'auto_install': False,
    'qweb': [
    ],
    'application': True,
}
