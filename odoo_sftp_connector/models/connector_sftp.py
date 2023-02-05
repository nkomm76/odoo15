# -*- coding: utf-8 -*-

from odoo import models, fields, api
import pysftp

import logging
_logger = logging.getLogger(__name__)


class SFTPConnection(models.Model):
    _name = 'sftp.connection'
    _description = 'SFTP Connection'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    host = fields.Char(string='Host', required=True, tracking=True)
    port = fields.Integer(required=True, default=22, tracking=True)
    username = fields.Char(required=True, tracking=True)
    password = fields.Char()
    private_key = fields.Text('Private Key', help='Copy your private key here!')
    host_key = fields.Text('Host Key')
    ignore_host_key = fields.Boolean()
    transport = fields.Binary(store=False)
    client = fields.Binary(store=False)

    message = fields.Text('Message', tracking=True)
    kanban_state = fields.Selection([
        ('normal', 'Not Connected'),
        ('done', 'Connected'),
        ('blocked', 'Failed')], string='Status',
        copy=False, default='normal', readonly=1, tracking=True)

    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Connection name must be unique.'),
    ]

    def test_sftp_connection(self):
        try:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            host = self.host or "demo.wftpserver.com"
            password = self.password or False
            username = self.username or "demo-user"

            with pysftp.Connection(host=host, username=username, password=password, cnopts=cnopts) as sftp:
                _logger.info("Successfully connected to SFTP server")
                self.message = "Successfully connected to SFTP server"
                self.kanban_state = 'done'
                sftp.close()

        except Exception as e:
            message = e.args
            _logger.exception("Failed to connect to SFTP server: " + str(message))
            self.message = "Failed to connect to SFTP server: " + str(message)
            self.message_post(body="Failed to connect to SFTP server: " + str(fields.Datetime.now()))
            self.kanban_state = 'blocked'

    def send_file(self, pdf_file, remote_path):
        host = self.host or "demo.wftpserver.com"
        password = self.password or False
        username = self.username or "demo-user"

        if self.private_key:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys.load(self.private_key)
        else:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
        try:
            with pysftp.Connection(host=host, username=username, password=password,
                                   cnopts=cnopts) as sftp:
                sftp.putfo(pdf_file, remote_path)
            pdf_file.close()
            _logger.info("File uploaded successfully")
            return True
        except Exception as e:
            _logger.exception('Exception! Error uploading file ' + str(e))
            return 'Exception! Error uploading file ' + str(e)
