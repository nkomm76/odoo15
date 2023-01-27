# -*- coding: utf-8 -*-

{
    "name": "SFTP Connections",
    "summary": "Provides SFTP Connection settings",
    "description": "Input the credentials of sftp server to create a connection for data export.",
    "version": "15.0.0",
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

