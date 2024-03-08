# -*- coding: utf-8 -*-

{
    "name": "Product Tracking HC",
    "version": "16.0.1.0",
    "category": "Stock",
    "description": "Custom lot producing id-s and serial/lot numbers for Hansacandle. Lot based tracking and reservation. Also includes partner purchase delivery method.",
    "summary": "Custom numberings for Hansacandle",
    "depends": [
        "stock",
        "mrp",
        "account_invoice_reports_hc",
        # purchase delivery method related dependencies.
        "delivery",
        "purchase",
    ],
    "data": [
        "views/report_events.xml",
        "views/stock_picking_views.xml",
        "views/report_lot_barcode.xml",
        "views/picking_type_views.xml",
        # purchase delivery method related views
        "views/purchase_views.xml",
        "views/res_partner_views.xml"
    ],
    "license": "OPL-1",

    # Author
    "author": "IMPACTIC OÜ",
    "website": "https://www.estpos.ee",

    # Technical
    "application": False,
}