from odoo import SUPERUSER_ID
from odoo.api import Environment

def migrate(cr, version):
    env = Environment(cr, SUPERUSER_ID, {})

    # Force-uninstall the unwanted module before Odoo 17 loads
    module_name = 'beone_sub_draft_invoice'
    module = env['ir.module.module'].search([('name', '=', module_name)], limit=1)
    if module and module.state in ('installed', 'to upgrade'):
        module.write({'state': 'uninstalled'})
