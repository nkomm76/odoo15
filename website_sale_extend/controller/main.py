# -*- coding: utf-8 -*-

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
import base64
from odoo import fields, http, SUPERUSER_ID, tools, _


class WebsiteSaleFilesUpload(WebsiteSale):

    @http.route(['/shop/add_attachment'], type='http', auth="public", website=True,
                sitemap=False)
    def add_attachments(self, **post):
        order = request.website.sale_get_order()
        files = request.httprequest.files.getlist('attachment')
        for file in files:
            attachment_ids = request.env['ir.attachment']
            name = file.filename
            attachment = file.read()
            if attachment:
                attachment_ids.sudo().create({
                    'name': name,
                    'is_temporary': True,
                    'res_name': name,
                    'type': 'binary',
                    'res_model': 'sale.order',
                    'res_id': order.id,
                    'datas': base64.b64encode(attachment),
                })
        return request.redirect("/shop/payment")

    @http.route(['/shop/attachment/delete'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def delete_attachment(self, attachment_id, **kw):
        removed = False
        order = request.website.sale_get_order()
        if attachment_id:
            removed = request.env['ir.attachment'].browse(int(attachment_id)).unlink()
        return {'removed': removed, 'attachment_count': order.attachment_count}
