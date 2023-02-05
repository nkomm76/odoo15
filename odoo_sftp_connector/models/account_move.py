from odoo import models, fields, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_sent = fields.Boolean('Invoice Sent?', copy=False, help="This shows if invoice is sent to SFTP server or not.")