# Copyright to The City Law Firm
{
    'name': "employeesinfo",
    'summary': """
        add more info for employees""",

    'description': """
    add more info for employee""",
    'author': "Mutn",
    'website': "www.mutn.tech",
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_skills','hr_holidays','project','hr_timesheet','hr_timesheet_attendance','litigation','hr_attendance','survey','account','sales_team'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/partner.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False
}
