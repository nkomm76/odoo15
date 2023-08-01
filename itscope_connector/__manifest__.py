# -*- coding: utf-8 -*-
{
    'name': "ITscope Connector",

    'summary': """Connect Odoo instance with ITscope""",

    'description': """
        - Fetch Product Details by ITScope ID
        - Website Product Page Changes
    """,

    'author': "aleemcahn",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'website_sale', 'stock'],
    # 'external_dependencies': {'python': ['pycountry']},

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/message_wizard.xml',
        'views/product_template_views.xml',
        'views/res_config_setting_views.xml',
        'views/templates.xml',
    ],

}
