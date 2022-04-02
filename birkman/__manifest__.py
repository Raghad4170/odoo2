# Copyright to Mutn
{
    'name': "birkman",
    'summary': """birkman""",
    'description': """birkman""",
    'sequence': -111,
    'author': "Mutn",
    'website': "www.mutn.tech",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','website','sale','parentid','sales_team'],
    'license': 'LGPL-3',
    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
#         'views/views.xml',
        'views/birkman.xml',
        'views/portal.xml',
        'data/mail.xml',
        'data/sale.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}

