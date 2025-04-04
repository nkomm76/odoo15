from odoo import SUPERUSER_ID
from odoo.api import Environment

def migrate(cr, version):
    from odoo.api import Environment

    env = Environment(cr, SUPERUSER_ID, {})

    module_name = 'beone_sub_draft_invoice'  # Replace with your target module

    module = env['ir.module.module'].search([('name', '=', module_name)], limit=1)
    if module and module.state == 'installed':
        module.button_immediate_uninstall()
