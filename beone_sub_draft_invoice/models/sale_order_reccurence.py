# -*- coding: utf-8 -*

from odoo import models, fields


class SaleOrderRecurrence(models.Model):
    _inherit = 'sale.temporal.recurrence'

    draft_invoice = fields.Boolean('Draft invoice', help='Check this if you want that the invoices created with this '
                                                         'recurrence to be not automatically posted', default=False)
