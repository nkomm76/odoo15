from odoo import models, fields, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_sent = fields.Boolean('Invoice Sent?', copy=False, help="This shows if invoice is sent to SFTP server or not.")
    invoice_date_sub = fields.Datetime(string='Date for Subscription', default=lambda self: fields.Datetime.now(),
                                       readonly=True,
                                       index=True, copy=False,
                                       states={'draft': [('readonly', False)]})

    def _post(self, soft=True):
        posted = super()._post(soft)
        for invoice in self.filtered(lambda move: move.is_invoice(include_receipts=True)):
            if invoice.is_sale_document(include_receipts=True):
                invoice.invoice_date_sub = fields.Datetime.now()
        return posted