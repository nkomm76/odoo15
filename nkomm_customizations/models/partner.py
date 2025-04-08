# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sequence_number = fields.Char(required=True, copy=False, readonly=False, index=True, default=lambda self: _('New'))
    digital_invoice = fields.Boolean(default=False, string="Digitale Rechnung")
    updated = fields.Boolean(default=False)

    @api.onchange('is_company')
    def _onchange_contact_is_company(self):
        for i in self:
            if i.is_company:
                i.title = False

    @api.onchange('parent_id')
    def _onchange_nkom_parent_id(self):
        if self.parent_id:
            self.sequence_number = self.parent_id.sequence_number

    @api.model
    def create(self, vals):
        if vals.get('sequence_number', _('New')) == _('New'):
            if 'parent_id' in vals and vals.get('parent_id', False):
                parent_id = self.browse(vals['parent_id'])
                vals['sequence_number'] = parent_id.sequence_number
            else:
                vals['sequence_number'] = self.env['ir.sequence'].next_by_code('res.partner') or _('New')
        return super(ResPartner, self).create(vals)
