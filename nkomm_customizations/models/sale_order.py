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

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        res = super()._prepare_invoice_line(**optional_values)
        description = res.get('name', '')
        if self.temporal_type == 'subscription' or self.order_id.subscription_management == 'upsell':
            description = self.name
        res.update({
            'name': description,
        })
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        if 'next_invoice_date' in vals and not vals['next_invoice_date'] and order.is_subscription:
            raise ValidationError("Bitte fügen Sie das Datum des Vertragsbeginns für die Abonnementprodukte hinzu.")
        else:
            return order

    @api.onchange('next_invoice_date')
    def _onchange_next_invoice_date(self):
        for order in self:
            if order.invoice_count == 0:
                order.start_date = order.next_invoice_date

    def _compute_l10n_din5008_template_data(self):
        """Add Customer Number to the template data"""
        res = super(SaleOrder, self)._compute_l10n_din5008_template_data()
        for record in self:
            if record.partner_id:
                data = record.l10n_din5008_template_data
                if record.user_id and record.user_id.phone:
                    data.append((_("Telefon"), record.user_id.phone or record.user_id.mobile))
                data.append((_("Kundennummer"), record.partner_id.sequence_number))
                record.l10n_din5008_template_data = data
        return res
