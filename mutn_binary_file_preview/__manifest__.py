# -*- coding: utf-8 -*-
{
    'name': "Document Preview",

    'summary': """
        Document Preview allows users to preview a document without downloading it that leads to saving
         time and storage of users.
        """,

    'description': """
        pdf attachment preview,
    """,

    'author': "Mutn",

    'license': 'LGPL-3',

    'website': "www.mutn.tech",

    'category': 'Tools',


    'version': '15.0.1.0.0',

    'depends': ['base', 'web', 'mail'],

     'data': [
     ],
     'qweb': ['static/src/xml/mutn_binary_preview.xml',
     ],

    'assets': {
        'web.assets_backend': [
            'mutn_binary_file_preview/static/src/js/DocumentViewerWidget.js',
            'mutn_binary_file_preview/static/src/js/mutn_binary_preview.js',
        ],
        'web.assets_qweb': ['mutn_binary_file_preview/static/src/xml/mutn_binary_preview.xml',
                            'mutn_binary_file_preview/static/src/xml/Viewer.xml'],
    },
}
