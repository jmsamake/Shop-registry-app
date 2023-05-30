# -*- coding: utf-8 -*-

{
    'name': "Registry App",
    'summary': """This is the registry app Summary""",
    'description': """
        Long description of module's purpose
    """,
    'sequence': -51,
    'version': '15.0.1.1.0',
    'author': 'Odoo SA,Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "http://www.cybrosys.com",
    'category': 'Uncategorized',
    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'product', 'website', 'portal'],
    # always loaded
    'data': [
        'security/security.xml',
        'security/registry_app_users_security.xml',
        'security/registry_app_shops_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/registry_app_website_registry_app_template.xml',
        'views/login_form.xml',
        # 'views/user_inherit.xml',
        'report/report_template_custom_header.xml',
        'report/registry_app_report.xml',
        'report/registry_app_report_template.xml',
        'views/registry_app_website_menu_views.xml',
        'views/registry_app_website_cooperative_template.xml',
        'views/registry_app_website_products_template.xml',
        'views/registry_app_website_client_template.xml',
        'views/registry_app_website_sms_broadcast.xml',
        'views/registry_app_website_shops.xml',
        'views/registry_app_portal_view.xml',
        'views/res_config_settings.xml',
        'data/auto_time_check.xml',
        'data/registry_log_closed.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'registry_app/static/src/css/style.css',
            # 'registry_app/static/src/css/menu_lock.css',
            'registry_app/static/src/js/sale_cust.js',
            'registry_app/static/src/js/main_navbar_hide.js',
            # 'registry_app/static/src/js/systray.js',
            'registry_app/static/src/js/test.js',
            # 'registry_app/static/src/js/lock_action.js',
            # 'registry_app/static/src/js/security_pin.js',
        ],
        'web.assets_frontend': [
            'registry_app/static/src/css/style.css',
            'registry_app/static/src/js/main_navbar_hide.js',
        ],
        'web.assets_qweb': [
            'registry_app/static/src/xml/templates.xml',
            'registry_app/static/src/xml/systray.xml',
            'registry_app/static/src/xml/tree_button.xml',
            # 'registry_app/static/src/xml/menu_lock.xml',
        ]
    },
    'installable': True,
    'application': True,
}
