# -*- coding: utf-8 -*-

{
    'name': 'Product Tags',
    'version': '16.0',
    'author': u'Estpos',
    'website': '',
    'category': 'Manufacturing',
    'depends': [
        'product',
        'stock',
        # 'product_configurator',
    ],
    'data': [
        'views/product_views.xml',
        'security/ir.model.access.csv',
    ],

    'description': u'''
Adds support to create products from a wizard and add them to a sales order.
''',
}
