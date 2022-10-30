# -*- coding: utf-8 -*-

import base64

from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    base_url = fields.Char(related='company_id.base_url', readonly=False)
    api_account_id = fields.Char(related='company_id.api_account_id', readonly=False)
    api_access_id = fields.Char(related='company_id.api_access_id', readonly=False)
    api_key = fields.Char(related='company_id.api_key', readonly=False)

    def generate_api_key(self):
        api_key = ""
        if self.api_account_id and self.api_access_id:
            base64_key = base64.b64encode(bytes(f"{self.api_account_id}:{self.api_access_id}", 'utf-8'))  # bytes
            base64_str = base64_key.decode('utf-8')
            api_key = base64_str
        self.company_id.api_key = api_key

