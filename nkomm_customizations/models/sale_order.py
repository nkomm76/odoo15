from odoo import models, fields, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    start_subscription_on = fields.Datetime(string="Vertragsbeginn")
    is_recurring_order = fields.Boolean(compute='_compute_is_recurring_order')

    def _compute_is_recurring_order(self):
        for order in self:
            is_recurring_order = False
            if any(line.product_id.recurring_invoice for line in order.order_line):
                is_recurring_order = True
            order.is_recurring_order = is_recurring_order

    def _compute_l10n_de_template_data(self):
        """Add Customer Number to the template data"""
        res = super(SaleOrder, self)._compute_l10n_de_template_data()
        for record in self:
            if record.partner_id:
                data = record.l10n_de_template_data
                data.append((_("Kundennummer"), record.partner_id.sequence_number))
                record.l10n_de_template_data = data
        return res
