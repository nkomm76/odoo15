# -*- coding: utf-8 -*-
{
    'name': 'Website Files Upload',
    'version': '15.0.1',
    'summary': 'Upload Multiple Files With E-commerce Order',
    'description': 'Option To Upload Files In Website',
    'author': 'aleemcaan',
    'depends': [
        'website_sale',
        'sale_management',
        'payment',
    ],
    'data': [
        'views/website_sale_templates.xml',
        'views/sale_order_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_sale_extend/static/src/js/attachment.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
