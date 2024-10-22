from odoo import api,fields,models
from odoo import http
import requests
import logging

_logger = logging.getLogger(__name__)


class ResProductPriceList(models.Model):
	_inherit='product.pricelist.item'

	pd_id=fields.Integer("Pipedrive Pricelist ID",readonly=True, copy=False)

