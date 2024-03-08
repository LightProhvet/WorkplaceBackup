# -*- coding: utf-8 -*-

{
    'name': 'Configurable Products',
    'version': '16.0',
    'author': u'Estpos',
    'website': '',
    'category': 'Manufacturing',
    'depends': [
        'sale_stock',
        'stock',
        'sale',
        'product',
        'mrp',
        'product_configurator_tags',
        'account',
    ],
    'data': [
        'views/type_test.xml',
        'views/product_configurator_templates_view.xml',
        'views/configurator_template_type.xml',
        'views/sale_view.xml',
        'views/configurator_sequence.xml',
        'views/product_configurator_view.xml',
        'views/product_views.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'product_configurator/static/src/components/**/*',
        ],
        'web.assets_frontend': [
        ],
    },
    'description': u'''
Adds support to create products from a wizard and add them to a sales order.
''',
}
