# Copyright to The City Law Firm
{
    'name': "balagh",
    'summary': """balagh messages""",
    'description': """balagh messages""",
    'sequence': -111,
    'author': "Mutn",
    'website': "www.mutn.tech",
    'version': '0.1',
    'depends': ['base','portal','website','parentid','product','sales_team'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/portal.xml',
        'data/mail_message.xml',
        'data/sale_message.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_frontend': [
            'balagh/static/src/js/balagh.js',
        ],
    }

}
