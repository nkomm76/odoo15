import re
from odoo import api,fields,models
from odoo.exceptions import Warning, UserError
from odoo import http, tools
import requests
import base64
import json
import logging
from binascii import Error as binascii_error
_image_dataurl = re.compile(r'(data:image/[a-z]+?);base64,([a-z0-9+/\n]{3,}=*)\n*([\'"])(?: data-filename="([^"]*)")?', re.I)



_logger = logging.getLogger(__name__)

class ResProduct(models.Model):
	_inherit='mail.activity.type'




	pd_activity_type=fields.Selection([('call','Call'), ('meeting','Meeting'),('task','Task'),
									   ('deadline','Deadline'),('email','Email'),
									   ('lunch','Lunch')], default='meeting')


	pd_id=fields.Integer("Pipedrive ID")
