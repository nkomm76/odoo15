from odoo import models, fields, _


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    file_sent = fields.Boolean('File Sent?', help="This shows if the file is sent to SFTP server or not.")
    response_message = fields.Text('SFTP File Status')