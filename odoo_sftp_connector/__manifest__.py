# -*- coding: utf-8 -*-

{
    "name": "SFTP Connector",
    "summary": "Provides Connection with SFTP Server",
    "description": "User will be able to open a connection with SFTP server and export invoices/Bills/Credit notes to SFTP server",
    "version": "16.0.0",
    "category": "Base",
    "website": "",
    "author": "aleemcaan",
    "license": "AGPL-3",
    "depends": ['base', 'mail', 'account'],
    "external_dependencies": {
        "python": [
            'pysftp',
            'mock',
        ],
    },
    "data": [
        'security/ir.model.access.csv',
        'views/connector_sftp_view.xml',
        'views/sftp_export_views.xml',
        'views/log_books_views.xml',
    ],

    "application": False,
    "installable": True,
}

