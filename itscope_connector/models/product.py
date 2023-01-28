# -*- coding: utf-8 -*-
import json
import ast

import requests
import logging
import base64
# import pycountry

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    itscope_id = fields.Char(string="ITscope ID", copy=False)
    stock_available_qty = fields.Float(string="Stock Available Quantity", readonly=True)
    stock_status = fields.Selection(selection=[
        ('1', 'auf Lager'),
        ('2', 'im Zulauf'),
        ('3', 'im Außenlager'),
        ('4', 'auftragsbezogene Bestellung'),
        ('6', 'nicht verfügbar'),
        ('8', 'Status unbekannt'),
    ], string='Verfügbarkeitsstatus', readonly=True, copy=False, tracking=True)
    response_text = fields.Text(string="ITscope Response", copy=False)
    last_updated = fields.Datetime("Last Updated", copy=False)
    pdf_datasheet = fields.Binary("Standard PDF Datasheet", copy=False)
    html_datasheet = fields.Text(string="Standard-Html-Datenblatt", copy=False)
    name_pdf_datasheet = fields.Char('PDF Name', default='Standard-PDF-Datasheet.pdf', size=32)

    def action_get_product_html_details(self):
        for product in self:
            if not product.html_datasheet and product.response_text:
                try:
                    response_text = ast.literal_eval(product.response_text)
                    if isinstance(response_text, dict):
                        it_product = response_text.get('product', [])
                        if len(it_product) == 1:
                            html_datasheet = it_product[0].get('standardHtmlDatasheet', '')
                            if html_datasheet:
                                product.html_datasheet = html_datasheet
                except Exception as e:
                    _logger.error(f"HTML Error: {e}")

    def action_get_product_details(self):
        product_id = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
        if product_id:
            res = product_id.get_product_details()
            if res.get('success', False):
                self.message_post(body=f"ITscope: Product Details Updated on: {res.get('last_updated', False)}")
            else:
                return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def action_get_product_details(self):
        res = self.get_product_details()
        if res.get('success', False):
            self.product_tmpl_id.message_post(body=f"ITscope: Product Details Updated on: {res.get('last_updated', False)}")
        else:
            return res

    def get_request_response(self, url):
        """get the request and return the response"""
        url = url
        payload = ""
        headers = {
            'Accept': 'application/json, application/xml, application/zip',
            'Accept-Language': 'de',
            'Authorization': f'{self.env.company.api_key}'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        return json.loads(response.text)

    def get_product_details(self):
        """get the product details"""
        if not self.env.company.base_url:
            raise ValidationError("ITscope API ist nicht konfiguriert! Bitte nehmen Sie die Konfiguration für ITscope in den Allgemeinen Einstellungen vor")
        url = f"{self.env.company.base_url}/products/id/{self.itscope_id}/standard.json?realtime=false"
        json_response = self.get_request_response(url)
        self.response_text = json_response

        product_list = json_response.get('product', [])
        message = json_response.get('message', [])

        image = False
        pdf = False
        product_price = ''
        supplier_item_price = ''
        supplier_item_stock = ''
        supplier_item_stock_availability = ''
        if len(product_list) > 0:

            # Product
            product_dict = product_list[0]

            # Product Image
            image_url = product_dict.get('image1', '')
            if image_url:
                image = self.get_file_from_url(image_url)

            # Html Content URL
            html_url = product_dict.get('standardHtmlDatasheet', '')

            # Product PDF
            pdf_url = product_dict.get('standardPdfDatasheet', '')
            if pdf_url:
                pdf = self.get_file_from_url(pdf_url)

            # Product Details
            product_name = product_dict.get('productNameWithManufacturer', '')
            product_description = product_dict.get('longDescription', '')

            # Product Suppliers
            product_supplier_info_list = product_dict.get('supplierItems', {})

            # Product Supplier Detail
            if product_dict.get('priceSupplierItemId'):
                supplier_item_dict = next(item for item in product_supplier_info_list if item.get('id', '') == product_dict.get('priceSupplierItemId', ''))
            else:
                supplier_item_dict = product_supplier_info_list[0]

            if supplier_item_dict:
                # Product Supplier Price Info
                supplier_item_price = supplier_item_dict.get('price', '')
                product_price = supplier_item_dict.get('priceCalc', '')

                # Product Suppliers Stock Info
                supplier_item_stock_availability = supplier_item_dict.get('stockStatus', '')
                supplier_item_stock = supplier_item_dict.get('stock', '')

                # Create or get partner
                # partner_id = self.create_or_get_company(supplier_item_dict)
                # if partner_id:
                #     supplier_vals = {
                #         'min_qty': 1,
                #         'name': partner_id.id,
                #         'product_name': supplier_item_dict.get('productName', ''),
                #         'price': float(supplier_item_dict.get('price', 0)),
                #         'product_tmpl_id': self.product_tmpl_id.id,
                #     }
                #
                #     # Create Supplier Item
                #     self.env['product.supplierinfo'].sudo().create(supplier_vals)

            last_updated = fields.Datetime.now()
            product_details = {
                'last_updated': last_updated,
                'detailed_type': 'product',
                'image_1920': image,
                'html_datasheet': html_url,
                'pdf_datasheet': pdf,
                'name': product_name,
                'description_sale': product_description,
                'description_purchase': product_description,
                'list_price': product_price,
                'standard_price': supplier_item_price,
                'stock_available_qty': float(supplier_item_stock),
                'stock_status': supplier_item_stock_availability,
            }

            # Update the Product Details
            updated = self.sudo().update(product_details)
            _logger.info(f"ITscope: Product Details Successfully Updated {product_details}")
            return {
                'success': True,
                'updated': updated,
                'last_updated': last_updated
            }
        elif message:
            _logger.info("ITscope Message: " + message)
            return self.show_message(message)

    # def create_or_get_company(self, supplier_item_dict=None):
    #     """If Partner already exists return partner if not create and return partner"""
    #     partner_exists = self.env['res.partner'].sudo().search(
    #         [('itscope_supplier_id', '=', supplier_item_dict.get('supplierId', ''))])
    #
    #     if partner_exists:
    #         return partner_exists
    #
    #     url = f"{self.env.company.base_url}/company/distributor/company.json"
    #     json_response = self.get_request_response(url)
    #     company_list = json_response.get('company', [])
    #     message = json_response.get('message', [])
    #
    #     partner_id = self.env['res.partner'].sudo()
    #     if company_list and not partner_id:
    #         supplier = next(item for item in company_list if item.get('supplier', '').get('id', '') == supplier_item_dict.get('supplierId', ''))
    #         if supplier:
    #             country_id = False
    #             code = supplier.get('country')
    #             if code and len(code) > 2:
    #                 country_data = pycountry.countries.get(alpha_3=code)
    #                 if country_data:
    #                     code = country_data.alpha_2
    #             country = self.env['res.country'].sudo().search([('code', '=', code)])
    #             if country:
    #                 country_id = country.id
    #
    #             partner_vals = {
    #                 'company_type': 'company',
    #                 'name': supplier.get('name', ''),
    #                 'street': supplier.get('street', ''),
    #                 'zip': supplier.get('zip', ''),
    #                 'city': supplier.get('city', ''),
    #                 'country_id': country_id,
    #                 'itscope_supplier_id': supplier_item_dict.get('supplierId', ''),
    #             }
    #             partner = self.env['res.partner'].sudo().create(partner_vals)
    #             if partner:
    #                 partner_id = partner
    #         return partner_id
    #
    #     else:
    #         _logger.info("ITscope Message: " + message)
    #         return partner_id

    def show_message(self, message):
        """Show the message in wizard"""
        return {
            'type': 'ir.actions.act_window',
            'name': _("Response Status"),
            'res_model': 'feedback.wizard',
            'view_mode': 'form',
            'context': {'default_message': message},
            "target": "new",
        }

    def get_file_from_url(self, url):
        """Get Data of File"""
        data = ""
        try:
            data = base64.b64encode(requests.get(url.strip()).content).replace(b"\n", b"")
        except Exception as e:
            _logger.warning("Can’t load the file from URL %s" % url)
            logging.exception(e)
        return data
