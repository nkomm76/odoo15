from odoo import models, fields, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _compute_l10n_din5008_template_data(self):
        """Add Customer Number to the template data"""
        res = super(PurchaseOrder, self)._compute_l10n_din5008_template_data()
        for record in self:
            if record.partner_id:
                data = record.l10n_din5008_template_data
                data.append((_("Kundennummer"), record.partner_id.sequence_number))
                record.l10n_din5008_template_data = data
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _get_product_purchase_description(self, product_lang):
        self.ensure_one()
        name = f"{product_lang.display_name}!!"
        if product_lang.description_purchase:
            name += '\n' + product_lang.description_purchase

        return name
