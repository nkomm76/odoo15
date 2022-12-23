# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sequence_number = fields.Char(required=True, copy=False, readonly=False, index=True, default=lambda self: _('New'))
    digital_invoice = fields.Boolean(default=False, string="Digitale Rechnung")
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

    @api.onchange('is_company')
    def _onchange_contact_is_company(self):
        for i in self:
            if i.is_company:
                i.title = False

    @api.model
    def create(self, vals):
        if vals.get('sequence_number', _('New')) == _('New'):
            vals['sequence_number'] = self.env['ir.sequence'].next_by_code('res.partner') or _('New')
        result = super(ResPartner, self).create(vals)
        return result
