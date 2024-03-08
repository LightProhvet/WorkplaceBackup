{
    'name': 'Stock Secondary Unit Extended',
    'version': '16.0.0.1',  # TODO: make stock.line secondary quantities and also product all sec qty-s.
    'author': u'IMPACTIC OÜ',
    'website': 'https://impactic.ee',
    "description": "Showing secondary unit instead of primary unit on reports. Adding text fields to the stock picking delivery sheets.",
    "summary": "Secondary unit of measurement customisations for the stock module",
    'depends': [
        "stock",
        "product_secondary_unit",
        "stock_secondary_unit",
    ],
    'data': [
        "report/report_deliveryslip.xml",
        "report/stock_picking_actions.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
    ],

    "application": False,
}
