# -*- coding: utf-8 -*-

{
    'name': 'FilterPlus Sales',
    'version': '14.0.0.7',
    'author': u'IMPACTIC OÜ',
    'website': 'https://impactic.ee',
    'category': 'Sales',
    'depends': [
        'account',
        'account_intrastat',
        'contacts',
        'l10n_ee',
        'mrp',
        'sale_management',
        'purchase',
        'report_html_pop_up',
        'stock_display_so_section',
        'website_pakiautomaadid',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/res_partner.xml',
        'views/account.xml',
        'views/production.xml',
        'views/sale.xml',

        'report/report_deliveryslip_inherit.xml',
        # 'report/report_invoice_document.xml',
        'report/report_picking_inherit.xml',
        'report/report_saleorder_document.xml',
    ],

    'description': u'''
This module adds additional fields to costumers.
''',
}
