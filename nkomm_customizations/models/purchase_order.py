from odoo import models, fields, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _compute_l10n_de_template_data(self):
        """Add Customer Number to the template data"""
        res = super(PurchaseOrder, self)._compute_l10n_de_template_data()
        for record in self:
            if record.partner_id:
                data = record.l10n_de_template_data
                data.append((_("Kundennummer"), record.partner_id.sequence_number))
                record.l10n_de_template_data = data
        return res
