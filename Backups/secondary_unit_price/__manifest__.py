# Copyright 2018-2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Secondary Unit Prices",
    "summary": "Various prices in secondary unit",
    "version": "16.1.0",
    "category": "Product",
    'website': 'https://impactic.ee',
    'author': u'IMPACTIC OÜ',
    'license': 'LGPL-3',
    "depends": [
        "sale_order_secondary_unit",
        "stock_secondary_unit",
        "purchase_order_secondary_unit",
        'account_move_secondary_unit',
    ],
    "data": [
        "views/account_move.xml",
        "views/purchase_views.xml",
        "views/sale_order_views.xml",
        # "views/stock_picking_views.xml",
        "report/purchase_reports.xml",
        "report/report_invoice.xml",
        "report/sale_report_templates.xml",
    ],
    'description': u'''
    Adds Prices to relevant units with secondary units. Secondary unit modules still to-do are:
    sale_stock_secondary_unit,
    purchaseaccount_moveproduct_product_stock_secondary_unit,
    edi_telema_secondary_unit,
    mrp_secondary_unit
    ''',
    "application": False,
    "installable": True,
    "auto_install": False,
}
