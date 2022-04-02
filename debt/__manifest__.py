# Copyright to Mutn
{
    'name': "Debt and violations in payroll",

    'summary': """""",

    'description': """""",
    'sequence': 1,
    'author': "Mutn",
    'website': "www.mutn.tech",
    'license': 'LGPL-3',
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','portal', 'utm', 'calendar','hr_payroll','hr_attendance','hr_holidays','hr','mail','hr_contract','hr_work_entry_contract','l10n_sa_hr_payroll','attendance','parentid'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/salary_rule.xml',
        'data/salary_rule_tech.xml',
        'data/salary_rule_mang.xml',
        'data/salary_rule_law.xml',
        'data/salary_rule_cons.xml',
        'data/violations_types.xml',
        'data/violation_cron.xml',
        'data/mail.xml',
        'views/views.xml',
        'views/violation_wizard.xml',
    ],
    'qweb': [
        "static/src/xml/custom_button.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'debt/static/src/js/action_call.js'
        ],
        'web.assets_qweb': [
            'debt/static/src/xml/custom_button.xml'
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False
}
