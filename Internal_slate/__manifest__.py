# Copyright to Mutn
{
    'name': "لوائح العمل الداخلية",
    'summary': """لوائح العمل الداخلية""",
    'description': """لوائح العمل الداخلية""",
    'sequence': -111,
    'author': "Mutn",
    'website': "www.mutn.tech",
    'license': 'LGPL-3',
    'category': 'Mutn',
    'version': '0.1',
    'depends': ['base','website','sale','sales_team','parentid'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/portal.xml',
        'views/report.xml',
        'data/sale_slate.xml',
        'data/mail.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'Internal_slate/static/src/js/custom.js'
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False
}
