# Copyright to The City Law Firm
{
    'name': "avatar",

    'summary': """""",

    'description': """""",
    'sequence': 1,
    'author': "Mutn",
    'website': "www.mutn.tech",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'portal','hr_attendance','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': True,
    'sequence': -9999,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_frontend': [
            'avatar/static/main.js',
            'avatar/static/leave.js',
            'avatar/static/style.scss',
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css',
        ],
    }

}
