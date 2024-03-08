# -*- coding: utf-8 -*-
{
    # Module information
    'name': 'Product Dimension',
    'category': 'Sales/Sales',
    'summary': '',
    'version': "16.1.1",
    'license': 'OPL-1',

    # Dependencies
    'depends': [
        'product',
    ],

    # Files are processed in the order of listing
    'data': [
        'views/res_config_settings_views.xml',
        'views/product_views.xml',
        'views/product_template_views.xml',
    ],

    # Odoo Store Specific
    'images': [
        '',
    ],

    # Author
    'author': u'IMPACTIC OÜ',
    'website': 'https://estpos.ee',

    # Technical
    'installable': True,
    'auto_install': False,
}
