from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    '''
		We will inherit res.config.settings to add
		pipedrive oauth URLS and Api url which are standard
	'''
    _inherit = 'res.config.settings'
    pd_authorize_url = fields.Char("Pipedrive Authorize URL")
    pd_token_url = fields.Char('Pipedrive Token URL')
    pd_api_url = fields.Char('Pipedrive API URL')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_pipedrive_connector.pd_authorize_url', self.pd_authorize_url)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_pipedrive_connector.pd_token_url', self.pd_token_url)
        self.env['ir.config_parameter'].sudo().set_param('pragmatic_pipedrive_connector.pd_api_url', self.pd_api_url)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['pd_authorize_url'] = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_authorize_url')
        res['pd_token_url'] = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_token_url')
        res['pd_api_url'] = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        return res
