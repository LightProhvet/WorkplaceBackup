# -*- coding: utf-8 -*-
{
    'name': 'Product Secondary Unit: Bundles Automatic Configuration',
    'version': '1.0',
    'author': u'IMPACTIC OÜ',
    'website': 'https://impactic.ee',
    'category': 'Hidden',
    'summary': 'Adds "Bundles" secondary unit template to secondary unit templates.',
    'description': "",
    'license': 'LGPL-3',
    'depends': [
        'product_secondary_unit_dimension',
        'product_standwood',
    ],
    'data': [
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'external_dependencies': {
    },
    'installable': True,
    'auto_install': False,
    'post_init_hook': '_auto_init_secondary_units',
    # 'uninstall_hook': '_uninstall_hook_ta_base',
}
