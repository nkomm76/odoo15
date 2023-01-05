# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sequence_number = fields.Char(required=True, copy=False, readonly=False, index=True, default=lambda self: _('New'))
    digital_invoice = fields.Boolean(default=False, string="Digitale Rechnung")
    updated = fields.Boolean(default=False)
    first_name = fields.Char(string='Vorname')
    last_name = fields.Char(string='Nachname')

    @api.onchange('last_name', 'first_name')
    def _onchange_first_last_name(self):
        for i in self:
            name = ''
            if i.first_name:
                name += i.first_name
            if i.last_name:
                name += ' ' + i.last_name
            i.name = name

    def _get_contact_name(self, partner, name):
        if partner.title:
            name = f"\n{partner.title.name} {name}"
        return "%s %s" % (partner.commercial_company_name or partner.sudo().parent_id.name, name)

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
