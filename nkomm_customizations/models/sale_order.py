# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    total_price_reduce_taxexcl = fields.Monetary(compute='_compute_total_price_reduce_taxexcl', string='Total', store=True)
    name = fields.Html(
        string="Description",
        compute='_compute_name',
        store=True, readonly=False, required=True, precompute=True)


    @api.depends('price_reduce_taxexcl', 'product_uom_qty')
    def _compute_total_price_reduce_taxexcl(self):
        for line in self:
            line.total_price_reduce_taxexcl = line.price_reduce_taxexcl * line.product_uom_qty if line.product_uom_qty else 0.0



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_sub = fields.Boolean(string='Is Subscription Order')
    maintenance_contract = fields.Char(string="Wartungsvertrag")

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
