# -*- coding: utf-8 -*-
{
    # Module information
    'name': 'Popup confirm wizard',
    'category': 'Human Resources/Employees',
    'summary': 'Unfinished',
    'version': "16.0.1.1.1",
    'license': 'OPL-1',

    # Dependencies
    'depends': [
        'base',
    ],

    # Files are processed in the order of listing
    'data': [
        'security/ir.model.access.csv',
        # popup wizard
        'wizard/popup_confirm_wizard.xml',
    ],

    "assets": {
        "web.assets_backend": [
            "/manufacturing_bonus_warmeston/static/src/js/*.js",
            "/manufacturing_bonus_warmeston/static/src/xml/*.xml",
        ],
    },

    # Author
    'author': u'IMPACTIC OÜ',
    'website': 'https://estpos.ee',

    # Technical
    'installable': True,
    'auto_install': False,

    # Description
    'description': """ 
    Warmeston specific bonus payment calculation based on manufacturing. Also adds analytic accounts to hr.work.location
    """
}
