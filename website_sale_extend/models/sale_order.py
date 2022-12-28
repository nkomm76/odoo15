# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    attachment_count = fields.Integer('Attachment Count',
                                      compute='_compute_attachment_count')
    attachments = fields.Many2many('ir.attachment', string="Attachments", compute="_compute_attachment_count")

    def _compute_attachment_count(self):
        """Compute the number of attachments"""
        for order in self:
            attachments = self.env['ir.attachment'].search(
                [('res_model', '=', 'sale.order'), ('res_id', '=', order.id)])
            order.attachments = attachments.ids
            order.attachment_count = len(attachments)

    def action_show_attachments(self):
        """View Attachment"""
        return {
            'name': _('Attachments'),
            'view_mode': 'kanban,form',
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'domain': [('res_model', '=', 'sale.order'), ('res_id', '=', self.id), ('is_temporary', '=', True)]
        }
