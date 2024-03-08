# -*- coding: utf-8 -*-

{
    "name": "Billing PDF reports",
    "version": "16.0.0.2",
    "category": "Accounting",
    "description": "Invoice report custom formatting. Includes a separate print action, paperformat, and custom templates and a few new fields.",
    "summary": "Invoice PDF reports for Hansacandle",
    "depends": [
        "base",
        "sale",
        "account",
        "partner_multi_gln",
    ],
    "data": [
        "report/account_report_hansa_candle.xml",
        "report/account_report_event_actions.xml",
        "report/stock_picking_report_hansa_candle.xml",
        "views/account_move_views.xml",
    ],
    "license": "OPL-1",

    # Author
    "author": "EST-POS OÜ",
    "website": "https://www.estpos.ee",

    # Technical
    "application": False,
}
