# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResConfigSettings(models.Model):
    _inherit = 'res.company'

    base_url = fields.Char(string='ITscope Base URL')
    api_account_id = fields.Char(string='Account ID')
    api_access_id = fields.Char(string='Access ID')
    api_key = fields.Char(string='API Key', readonly=True)

