from odoo import api,fields,models
from odoo import http
import requests
import logging


_logger = logging.getLogger(__name__)

class ResStage(models.Model):
	_inherit='crm.stage'

	#adding field
	pd_id=fields.Integer("Pipedrive Stage ID", copy=False)

