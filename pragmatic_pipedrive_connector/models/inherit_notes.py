from odoo import api,fields,models
from odoo.exceptions import Warning
from odoo import http
import requests
import base64
import json
import logging


_logger=logging.getLogger(__name__)

class ResNotes(models.Model):
	_inherit='mail.message'

	#adding fields
	pd_notes_id=fields.Integer("Pipedrive Notes ID", copy=False)
	pd_deal_id=fields.Integer("Pipedrive Ntes DEal ID", copy=False)


