# -*- coding: utf-8 -*-
{
    'name': "BEONE Subscription Draft Invoices",

    'summary': """
        Give back the ability to push subscription invoices in draft instead of posting them on Odoo 16
        """,

    'description': """
        Adding a check box to the recurrence item that allow you to specify that you want the invoices on that specific recurrence to be created in draft instead of posted
        """,

    'author': "Edwin BRASSEUR",
    'website': "http://www.beonegroup.be",

    'category': 'Sales/Subscriptions',
    'version': '16.0',
    'license': 'OPL-1',

    'price': 50.00,
    'currency': 'EUR',

    'depends': ['base', 'sale_subscription', 'sale_temporal'],

    'images': ['static/description/banner.gif'],

    'data': [
        'views/sale_temporal.xml',
    ],
}
