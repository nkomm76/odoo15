# -*- coding: utf-8 -*-
{
    'name': "N-Komm Extension",

    'summary': """Customizations related to Sales, Contact and Invoice""",

    'description': """
        - Customer Sequence Numbers
        - Customized Sales Reports
        - Customized Invoice Reports
        - Customized Purchase Reports
        - Sale Subscription Customzations
    """,

    'author': "aleemcahn",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'l10n_din5008', 'purchase', 'sale_subscription'],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        'data/data.xml',
        # 'views/ir_qweb.xml',
        'report/report_invoice.xml',
        'report/sale_report_templates.xml',
        'report/purchase_quotation_templates.xml',
        'report/purchase_order_templates.xml',
        'report/din5008_report.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/account_views.xml',
        # 'views/sale_subscription_view.xml',
    ],

}
