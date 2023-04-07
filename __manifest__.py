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
    'depends': ['base', 'web', 'product'],
    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/login_form.xml',
        'report/report_template_custom_header.xml',
        'report/registry_app_report.xml',
        'report/registry_app_report_template.xml',
        'data/auto_time_check.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'registry_app/static/src/js/sale_cust.js',
            'registry_app/static/src/css/style.css',
        ],
        'web.assets_qweb': [
            'registry_app/static/src/qweb/templates.xml',
        ]
    },
    'installable': True,
    'application': True,
}
