# -*- coding: utf-8 -*-

{
    'name': 'FilterPlus Sales OO Extension',
    'version': '14.0.0.0',
    'author': u'IMPACTIC OÜ',
    'website': 'https://impactic.ee',
    'category': 'Sales',
    "summary": "FilterPlus Sales Object Oriented Extension",
    'depends': [
        # 'account',
        # 'account_intrastat',
        # 'contacts',
        # 'l10n_ee',
        # 'mrp',
        # 'sale_management',
        # 'purchase',
        # 'report_html_pop_up',
        # 'stock_display_so_section',
        # 'website_pakiautomaadid', - are from sale_dagoterm
        'sale_dagoterm',
        # 'purchase_stock',
        # 'sale_stock',
        # 'account_inter_company_rules',
        'sale_purchase_inter_company_rules',
        'sale_purchase',
        # 'mrp_workorder_dagoterm',

    ],
    'data': [
        'views/production.xml',
        'views/sale.xml',
        'views/purchase.xml',
        'views/stock_views.xml',
    ],

    'description': u'''
This module adds object relations to sale order line, purchase, purchase order lines, picking, stock moves and ensures object relations
Also includes transfering original sale order client information through all of the workflow.
''',
}
