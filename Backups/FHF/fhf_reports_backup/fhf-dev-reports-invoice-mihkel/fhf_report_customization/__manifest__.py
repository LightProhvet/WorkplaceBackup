# -*- coding: utf-8 -*-

{
    'name': 'FHF Reports Layout',
    'version': '16.0.0.1',
    'author': u'EST-POS OÜ',
    'license': 'OPL-1',
    'website': 'https://estpos.ee',
    'category': 'Reports',
    'depends': [
        'base', 'web', "account"
    ],
    'data': [
        'views/fhf_layout.xml',
        'views/base_document_layout_views.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'fhf_report_customization/static/src/scss/main.css',
        ], },
    'description': u'FHF Report Customization',
}
