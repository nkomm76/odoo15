import logging

import requests
from odoo import fields, models, _
from odoo import http
from odoo.exceptions import UserError
import json

_logger = logging.getLogger(__name__)


class ResProduct(models.Model):
    _inherit = 'product.product'

    pd_prod_id = fields.Integer("Pipedrive Product ID", readonly=True, copy=False)
    pd_direct_code = fields.Integer("Pipedrive Direct Cost")
    pd_currency = fields.Char("Pipedrive currency", default='INR')

    def create_products(self, caller):
        _logger.info("*********EXPORTING FROM ODOO***************")
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri = '{0}%s' % (caller)
        uri_caller = uri.format(domain)
        _logger.info("******URI CALLER*********{}".format(uri_caller))
        # company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
        company_id = None
        user_id = self.env['res.users'].search([])
        for user in user_id:
            for company in user.company_ids:
                if company.access_token and company.refresh_token:
                    company_id = company
                    break
            if company_id:
                break

        # for company_id in user_id.company_ids:
        #     if company_id.access_token and company_id.refresh_token:
        #         company_id = company_id
        if company_id:

            for rec in self:
                headers = {}
                headers['Authorization'] = "Bearer " + company_id.access_token
                headers['content-type'] = 'application/json'
                payload = {
                    "name": rec.name,
                    "code": rec.default_code,
                    "prices": [{"currency": rec.pd_currency, "price": rec.lst_price,
                                "cost": rec.standard_price, "overhead_cost": rec.pd_direct_code}],

                }
                payload = json.dumps(payload)
                if company_id.access_token:
                    _logger.info("Access token Found")
                else:
                    raise UserError(_("Access Token not found!!!"))

                response = requests.post(url=uri_caller, data=payload, headers=headers, verify=False)
                _logger.info("RESPONSE IS-{}".format(response))
                data = response.json()
                _logger.info("**************14 {}".format(data))
                rec.write({'pd_prod_id': data.get('data').get('id')})

    def odoo_update_products(self, pd_prod_id):
        '''
        This function will update the product details in pipedrive
        :return: updates product data
        '''
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri = "{0}products/%s" % (pd_prod_id)
        uri_caller = uri.format(domain)

        # company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
        company_id = None
        user_id = self.env['res.users'].search([])
        for company_id in user_id.company_ids:
            if company_id.access_token and company_id.refresh_token:
                company_id = company_id
        if company_id:

            for rec in self:
                headers = {}
                headers['Authorization'] = "Bearer " + company_id.access_token
                headers['content-type'] = 'application/json'
                payload = {
                    'id': rec.pd_prod_id,
                    'name': rec.name,
                    'code': rec.default_code,
                    "prices": [{"currency": rec.pd_currency, "price": rec.lst_price,
                                "cost": rec.standard_price, "overhead_cost": rec.pd_direct_code}],
                }
                payload = json.dumps(payload)
                if company_id.access_token:
                    _logger.info("Access token Found")
                else:
                    raise UserError(_("Access Token not found!!!"))

                response = requests.put(url=uri_caller, data=payload, headers=headers, verify=False)
                data = response.json()
                _logger.info("**************15 {}".format(data))
                return data

    def check_product_exists(self, pd_prod_id):
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')

        uri = "{0}products/%s" % (pd_prod_id)
        uri_caller = uri.format(domain)

        # company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
        company_id = None
        user_id = self.env['res.users'].search([])
        for company_id in user_id.company_ids:
            if company_id.access_token and company_id.refresh_token:
                company_id = company_id
        if company_id:
            headers = {}
            headers['Authorization'] = "Bearer " + company_id.access_token
            headers['content-type'] = 'application/x-www-form-urlencoded'
            headers['Accept'] = 'application/json'
            if company_id.access_token:
                _logger.info("Access token Found")
            else:
                raise UserError(_("Access Token not found!!!"))
            response = requests.get(url=uri_caller, headers=headers, verify=False)
            prod_data = response.json()
            _logger.info("**************16 {}".format(prod_data))
            if prod_data:
                res = prod_data.get('data')
                if res:
                    if res['active_flag'] == True:
                        _logger.info("This product exists in pipedrive")
                        return True
                    else:
                        _logger.warning("This product does not exists in pipedrive")
                        return False

    def export_odoo_products(self):
        _logger.info("EXPORTING ODOO PRODUCT**********")
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri_caller = "{0}products".format(domain)
        # company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
        company_id = None
        user_id = self.env['res.users'].search([])
        for company_id in user_id.company_ids:
            if company_id.access_token and company_id.refresh_token:
                company_id = company_id
        if company_id:
            for rec in self:
                headers = {}
                headers['Authorization'] = "Bearer " + company_id.access_token
                headers['content-type'] = 'application/x-www-form-urlencoded'
                headers['Accept'] = 'application/json'
                payload = {
                    'name': rec.name,
                    'code': rec.default_code,
                }
                if company_id.access_token:
                    _logger.info("Access token Found")
                else:
                    raise UserError(_("Access Token not found!!!"))

                response = requests.post(url=uri_caller, data=payload, headers=headers, verify=False)
                prod_data = response.json()
                _logger.info("**************17 {}".format(prod_data))

    def filter_products(self):
        '''
        THis function wil filter products!!!
        :return:
        '''

        rec = self.env['product.product'].search([])
        for fetch in rec:
            _logger.info("FETCHING PRODUCTS FROM ODOO TO PIPEDIRVE")
            _logger.warning("No of records fetched are {}".format(len(rec)))
            fetch.export_products()

    def export_products(self):
        '''
        This function will export products from odoo to pipedrive
        :return:
        '''
        # first to check if product exists in pipedrive

        for rec in self:
            if rec.pd_prod_id:
                # This product is been imported from pipedrive
                return_val = self.check_product_exists(rec.pd_prod_id)
                if return_val:
                    # #Need to update the product i.e send odoo dict to pipedrive
                    updated_data = self.odoo_update_products(rec.pd_prod_id)
                else:
                    # Need to create the product in pipedrive
                    exp_data = self.create_products("products")
            else:
                # This product is been created from odoo which needs
                # to be imported to pipedrive'''
                self.create_products("products")
