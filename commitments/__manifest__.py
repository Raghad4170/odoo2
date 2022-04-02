# Copyright to The City Law Firm
{
    'name': "الإلتزام",
    'summary': """متابعة مدى إلتزام الشركات""",
    'description': """""",
    'author': "Mutn",
    'website': "www.mutn.tech",
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base','website'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/portal.xml',
        'report/report.xml',
        'report/summary.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'commitments/static/src/js/survey_commitment.js',
            'commitments/static/src/style.scss',
        ],

    },
    'installable': True,
    'application': True,
    'sequence': -9999,
}
