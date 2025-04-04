from odoo import SUPERUSER_ID
from odoo.api import Environment

def migrate(cr, version):
    env = Environment(cr, SUPERUSER_ID, {})

    # Force-uninstall the unwanted module before Odoo 17 loads
    module_name = 'beone_sub_draft_invoice'
    module = env['ir.module.module'].search([('name', '=', module_name)], limit=1)
    if module and module.state in ('installed', 'to upgrade'):
        module.write({'state': 'uninstalled'})

    SaleOrder = env['sale.order']

    # Find violating records
    bad_orders = SaleOrder.search([
        ('is_subscription', '=', True),
        ('state', '=', 'sale'),
        ('subscription_state', '=', '1_draft')
    ])

    for order in bad_orders:
        # Log or print to track (optional)
        print(f"Fixing sale order {order.name} (id={order.id}) with invalid subscription state")

        # Decide the right fix:
        # Option 1: Mark subscription as 3_progress (most common fix)
        order.subscription_state = '3_progress'

