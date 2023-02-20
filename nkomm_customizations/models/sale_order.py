# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    total_price_reduce_taxexcl = fields.Monetary(compute='_compute_total_price_reduce_taxexcl', string='Total', store=True)

    @api.depends('price_reduce_taxexcl', 'product_uom_qty')
    def _compute_total_price_reduce_taxexcl(self):
        for line in self:
            line.total_price_reduce_taxexcl = line.price_reduce_taxexcl * line.product_uom_qty if line.product_uom_qty else 0.0

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    start_subscription_on = fields.Date(string="Vertragsbeginn")
    is_recurring_order = fields.Boolean(compute='_compute_is_recurring_order')
    subscription_invoice_today = fields.Boolean(compute='_compute_subscription_invoice_today')

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        if 'start_subscription_on' in vals and not vals['start_subscription_on'] and any(line.product_id.recurring_invoice for line in order.order_line):
            raise ValidationError("Bitte fügen Sie das Datum des Vertragsbeginns für die Abonnementprodukte hinzu.")
        else:
            return order

    @api.onchange('order_line')
    def _compute_is_recurring_order(self):
        """Compute the if there is any line that has subscription product"""
        for order in self:
            is_recurring_order = False
            if any(line.product_id.recurring_invoice for line in order.order_line):
                is_recurring_order = True
            order.is_recurring_order = is_recurring_order

    def _compute_subscription_invoice_today(self):
        """Compute if the subscription is going to start for today (for Create Invoice button show/hide)"""
        for order in self:
            invoice_today = False
            date_today = fields.Date.context_today(self)
            if order.start_subscription_on == date_today or not order.is_recurring_order:
                invoice_today = True
            order.subscription_invoice_today = invoice_today

    def _prepare_subscription_data(self, template):
        values = super(SaleOrder, self)._prepare_subscription_data(template)
        date_contract = self.start_subscription_on
        recurring_invoice_day = date_contract.day
        recurring_next_date = self.env['sale.subscription']._get_recurring_next_date(
            template.recurring_rule_type, template.recurring_interval,
            date_contract, recurring_invoice_day
        )
        if 'date_start' in values:
            values['date_start'] = self.start_subscription_on
        if 'recurring_invoice_day' in values:
            values['recurring_invoice_day'] = recurring_invoice_day
        if 'recurring_next_date' in values:
            values['recurring_next_date'] = recurring_next_date
        values['start_subscription_on'] = self.start_subscription_on
        return values

    def _compute_l10n_de_template_data(self):
        """Add Customer Number to the template data"""
        res = super(SaleOrder, self)._compute_l10n_de_template_data()
        for record in self:
            if record.partner_id:
                data = record.l10n_de_template_data
                data.append((_("Kundennummer"), record.partner_id.sequence_number))
                record.l10n_de_template_data = data
        return res


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        """change the date start and first_invoice on confirmation"""
        res = super(SaleAdvancePaymentInv, self).create_invoices()

        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        if sale_orders:
            for order in sale_orders:
                sub_ids = self.env['sale.order.line'].search(
                    [('order_id', '=', order.id), ('subscription_id', '!=', False)]).mapped('subscription_id')
                sub_ids.write({
                    'date_start': fields.Date.context_today(self),
                    'start_subscription_on': fields.Date.context_today(self),
                    'first_invoice': True
                })
        return res


