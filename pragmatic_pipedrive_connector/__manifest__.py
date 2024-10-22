{
    'name': 'Odoo Pipedrive Connector',
    'version': '16.0.4',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'www.pragtech.co.in',
    'depends': ['base', 'sale', 'crm', 'mail'],
    'external_dependencies': {'python': ['requests']},
    'summary': 'Odoo Pipedrive Connector odoo pipedrive connector odoo pipedrive integration pipedrive app piepedrive module',
    'description': '''
Odoo Pipedrive Connector
========================    
<keywords>
odoo pipedrive connector
odoo pipedrive integration
pipedrive app
piepedrive module
    ''',
    'category': 'Services',
    'data': [
        # including all views
        "views/company_view.xml",
        "views/settings_view.xml",
        "views/partner_view.xml",
        "views/crm_view.xml",
        "views/product_view.xml",
        "views/activity_view.xml",
        "views/notes_view.xml",
        "views/product_pricelist_view.xml",
        "views/activity_type_view.xml",
        "views/crm_stage_view.xml",

        # including server actions
        "server_actions/export_contacts.xml",
        "server_actions/export_products.xml",
        "server_actions/export_deals.xml",
        "server_actions/export_activities.xml",

        # including cron for importing from pipedirve
        "cron/import_cron.xml",
        # for exporting
        "cron/export_contacts_cron.xml",
        "cron/export_activities_cron.xml",
        "cron/export_deals_cron.xml",
        "cron/export_products_cron.xml",
        # for refreshing
        "cron/refresh_token_cron.xml"
    ],
    'images': ['static/description/Animated-pipedrive-connector.gif'],
    # 'images': ['static/description/end-of-year-sale-main.jpg'],
    'live_test_url': 'https://www.pragtech.co.in/company/proposal-form.html?id=103&name=odoo-pipedrive-connector',
    'license': 'OPL-1',
    'price': 198,
    'currency': 'USD',
    'installable': True,
    'application': False,
    'auto_install': False,
    'external_dependencies': {'python': ['requests']}
}
