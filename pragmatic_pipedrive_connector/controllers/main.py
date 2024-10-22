import base64
import json
import logging

import requests
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class Pipedrive_connector(http.Controller):
    @http.route('/get_auth_code', type="http", auth="public", website=True)
    def get_auth_code(self, **kwarg):
        if kwarg.get('code'):
            '''Get access Token and store in object'''
            company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
            client_id = company_id.client_id
            client_secret = company_id.client_secret
            redirect_uri = company_id.redirect_uri
            headers = {}
            combined_key = ' '
            if client_id and client_secret:
                combined_key = client_id + ":" + client_secret
            else:
                _logger.info("client_id & client_secret invalid")
            encoded_key = base64.b64encode(bytes(combined_key, 'utf-8'))
            headers['Authorization'] = "Basic " + encoded_key.decode('utf-8')

            headers['content-type'] = 'application/x-www-form-urlencoded'
            payload = {
                'code': kwarg.get('code'),
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code',
            }
            pd_token_url = request.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_token_url')
            access_token = requests.post(pd_token_url, data=payload, headers=headers, verify=False)
            if access_token:
                parsed_token_response = json.loads(access_token.text)
                _logger.info("PARSED TOKEN RESPONSE FROM CONTROLLER IS {}".format(parsed_token_response))
                if parsed_token_response:
                    data_dict = {}
                    data_dict['access_token'] = parsed_token_response.get('access_token')
                    data_dict['refresh_token'] = parsed_token_response.get('refresh_token')
                    company_id.write(data_dict)
        else:
            return "Some issue in request, Try again. If issue persists please contact developer"
        return "You can close this window now"
