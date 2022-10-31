from odoo import models, fields, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _compute_l10n_de_template_data(self):
        """Add Customer Number to the template data"""
        res = super(AccountMove, self)._compute_l10n_de_template_data()
        for record in self:
            if record.partner_id:
                data = record.l10n_de_template_data
                data.append((_("Kundennummer"), record.partner_id.sequence_number))
                record.l10n_de_template_data = data
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

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
