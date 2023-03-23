# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, _, api


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    first_invoice = fields.Boolean(compute='compute_first_invoice_done', store=True)
    start_subscription_on = fields.Date(string="Vertragsbeginn", required=True)
    end_subscription_on = fields.Date(string="Vertragsende")

    @api.depends('invoice_count')
    def compute_first_invoice_done(self):
        for sub in self:
            first_invoice_done = True
            if sub.invoice_count == 0:
                first_invoice_done = False
            sub.first_invoice = first_invoice_done

    def _recurring_create_invoice(self, automatic=False, batch_size=20):
        """If invoices are created then go ahead and set first_invoice to True"""
        invoices = super(SaleSubscription, self)._recurring_create_invoice(automatic=automatic, batch_size=batch_size)
        sub_ids = invoices.mapped('invoice_line_ids').mapped('subscription_id')

        for sub in sub_ids:
            if not sub.first_invoice:
                sub.first_invoice = True

        # Close those subscriptions on which the end date is expired
        current_date = datetime.date.today()
        for subscription in self.search([('end_subscription_on', '<=', current_date)]):
            subscription.set_close()
        return invoices

    def _get_subscription_domain_for_invoicing(self, current_date, tags):
        """Override the domain and custom domain"""
        return [
            ('tag_ids', 'not in', tags.ids),
            '|',
            ('recurring_next_date', '<=', current_date),
            ('first_invoice', '=', False),
            ('start_subscription_on', '<=', current_date),
            ('end_subscription_on', '>=', current_date),
            ('template_id.payment_mode', '!=', 'manual'),
            '|',
            ('stage_category', '=', 'progress'),
            ('to_renew', '=', True),
        ]
    

