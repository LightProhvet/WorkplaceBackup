{
    'name': "Google Drive with OAuth 2.0",
    'name_vi_VN': "Google Drive với OAuth 2.0",

    'summary': """Support authentication with Google Drive using OAuth 2.0""",

    'summary_vi_VN': """Hỗ trợ xác thực với Google Drive sử dụng OAuth 2.0""",

    'description': """
Problem
=======
The module Google Drive integration will stop working after the 3rd October 2022 due to changes in Google Authentication API. See here: https://developers.googleblog.com/2022/02/making-oauth-flows-safer.html#disallowed-oob.

Key Features
============
* Support authentication with Google Drive using OAuth 2.0

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Vấn đề
======
Module Tích hợp Google Drive sẽ ngừng hoạt động từ ngày 3 tháng 10 năm 2022 do những thay đổi trong API xác thực của Google. Xem tại đây: https://developers.googleblog.com/2022/02/making-oauth-flows-safer.html#disallowed-oob.

Tính năng chính
===============
* Hỗ trợ xác thực với Google Drive sử dụng OAuth 2.0

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Tools',
    'version': '0.1',
    'depends': ['google_drive'],
    'data': [
        'views/res_config_settings.xml',
    ],
    'demo': [],
    'images' : [],
    'installable': True,
    'application': False,
    'auto_install': True,  # Set as True while upgrading to 15.0
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
