# -*- coding: utf-8 -*-
# Copyright to Mutn
{
    'name': "workTrip",

    'summary': """Allow employee to take work trip in attendance""",

    'description': """""",
    'sequence': -11,
    'author': "Mutn",
    'website': "www.mutn.tech",
    'category': 'Tools',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_attendance','parentid'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/views.xml',
        'views/template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'work_trip/static/src/scss/work_trip.scss',
            'work_trip/static/src/js/work_trip.js',
            'work_trip/static/src/js/trip_location.js',
            'work_trip/static/src/js/attendance_location.js',
            'work_trip/static/src/js/map.js',
            'work_trip/static/src/js/map2.js',
        ],
        'web.assets_qweb': [
            'work_trip/static/src/map.xml',
            'work_trip/static/src/attendance.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
