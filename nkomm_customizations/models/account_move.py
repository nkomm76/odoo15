# -*- coding: utf-8 -*-

from odoo import api, fields, models, Command, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, float_is_zero, date_utils, email_split, email_re, html_escape, is_html_empty
from odoo.tools.misc import formatLang, format_date, get_lang
from collections import defaultdict


class AccountMove(models.Model):
    _inherit = 'account.move'

    digital_invoice = fields.Boolean(related="partner_id.digital_invoice")
    invoice_date = fields.Date(string='Invoice/Bill Date', default=lambda self: fields.Datetime.now(), readonly=True,
                               index=True, copy=False,
                               states={'draft': [('readonly', False)]})
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

    def action_invoice_sent(self):
        """
        Set is_print based on digital_invoice set on partner
        """
        res = super(AccountMove, self).action_invoice_sent()
        ctx = res.get('context', False)
        if ctx:
            ctx['default_is_print'] = not self.digital_invoice
        return res

    def _compute_l10n_din5008_template_data(self):
        """Add Customer Number to the template data"""
        res = super(AccountMove, self)._compute_l10n_din5008_template_data()
        for record in self:
            if record.partner_id:
                data = record.l10n_din5008_template_data
                if record.user_id and record.user_id.phone:
                    data.append((_("Telefon"), record.user_id.phone or record.user_id.mobile))
                data.append((_("Kundennummer"), record.partner_id.sequence_number))
                if record.move_type == 'out_refund':
                    data = [tup for tup in data if tup[0] not in ('Fälligkeit', 'Due Date')]
                    data = [tup for tup in data if tup[0] not in ('Rechnungsnummer', 'Invoice No.')]
                    data.insert(0, (_("Gutschriftsnummer"), record.name))
                record.l10n_din5008_template_data = data
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    name = fields.Text(
        string='Label',
        compute='_compute_name', store=True, readonly=False, precompute=True,
        tracking=True,
    )

    def _get_computed_name(self):
        self.ensure_one()

        if not self.product_id:
            return ''

        if self.partner_id.lang:
            product = self.product_id.with_context(lang=self.partner_id.lang)
        else:
            product = self.product_id

        values = []
        if product.partner_ref:
            values.append(f"{product.partner_ref}!!")
        if self.journal_id.type == 'sale':
            if product.description_sale:
                values.append(product.description_sale)
        elif self.journal_id.type == 'purchase':
            if product.description_purchase:
                values.append(product.description_purchase)
        return '\n'.join(values)
