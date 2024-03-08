# -*- coding: utf-8 -*-

{
    "name": "Smart Timesheets",
    "version": "16.0.0.1",
    "category": "Project",
    "description": "Automatic allocated hour calculation, quicker task start options, and new Create on Order type.",
    "summary": "Timesheets optimization module.",
    "assets": {
        "web.assets_backend": [
            "smart_timesheets/static/src/js/timedate.js",
        ],
    },
    "depends": [
        "base",
        "sale_project",
        "hr_timesheet",
        "timesheet_grid",
    ],
    "data": [
        "views/product_views.xml",
        'views/project_views.xml',
        'views/analytic_line_views.xml',
        'wizard/project_task_create_timesheet_views.xml',
        "data/scheduled_actions.xml",
        #"views/sale_order_views.xml",
    ],
    "license": "OPL-1",

    # Author
    "author": "IMPACTIC OÜ",
    "website": "https://www.estpos.ee",

    # Technical
    "application": False,
}
