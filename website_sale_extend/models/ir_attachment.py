# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Attachment(models.Model):

    _inherit = "ir.attachment"

    is_temporary = fields.Boolean(string="Is temporary?")