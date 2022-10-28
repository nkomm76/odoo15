from odoo import api, fields, models


class MessageWizard(models.TransientModel):
    _name = 'feedback.wizard'
    _description = 'Feedback Wizard'

    message = fields.Text('Message', required=True)

    def action_ok(self):
        """ close wizard"""
        return {'type': 'ir.actions.act_window_close'}
