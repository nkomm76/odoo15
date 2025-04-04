import logging

import requests
from odoo import fields, models, _
from odoo.exceptions import Warning, UserError
from collections import defaultdict

_logger = logging.getLogger(__name__)


class ResActivity(models.Model):
    _inherit = 'mail.activity'

    pd_activity_id = fields.Integer("Pipedrive Activity ID", readonly=True, copy=False)

    # def action_feedback(self, feedback=False, attachment_ids=None):
    #     message = self.env['mail.message']
    #     if feedback and attachment_ids:
    #         self.write(dict(feedback=feedback, attachment_ids=attachment_ids))
    #     for activity in self:
    #         record = self.env[activity.res_model].browse(activity.res_id)
    #         record.message_post_with_view(
    #             'mail.message_activity_done',
    #             values={'activity': activity},
    #             subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_activities'),
    #             mail_activity_type_id=activity.activity_type_id.id,
    #         )
    #         message |= record.message_ids[0]
    #     self.update_activity()
    #     self.unlink()
    #     return message.ids and message.ids[0] or False

    def _action_done(self, feedback=False, attachment_ids=None):
        """ Private implementation of marking activity as done: posting a message, deleting activity
            (since done), and eventually create the automatical next activity (depending on config).
            :param feedback: optional feedback from user when marking activity as done
            :param attachment_ids: list of ir.attachment ids to attach to the posted mail.message
            :returns (messages, activities) where
                - messages is a recordset of posted mail.message
                - activities is a recordset of mail.activity of forced automically created activities
        """
        # marking as 'done'
        messages = self.env['mail.message']
        next_activities_values = []

        # Search for all attachments linked to the activities we are about to unlink. This way, we
        # can link them to the message posted and prevent their deletion.
        attachments = self.env['ir.attachment'].search_read([
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
        ], ['id', 'res_id'])

        activity_attachments = defaultdict(list)
        for attachment in attachments:
            activity_id = attachment['res_id']
            activity_attachments[activity_id].append(attachment['id'])

        for activity in self:
            # extract value to generate next activities
            if activity.chaining_type == 'trigger':
                Activity = self.env['mail.activity'].with_context(activity_previous_deadline=activity.date_deadline)  # context key is required in the onchange to set deadline
                vals = Activity.default_get(Activity.fields_get())

                vals.update({
                    'previous_activity_type_id': activity.activity_type_id.id,
                    'res_id': activity.res_id,
                    'res_model': activity.res_model,
                    'res_model_id': self.env['ir.model']._get(activity.res_model).id,
                })
                virtual_activity = Activity.new(vals)
                virtual_activity._onchange_previous_activity_type_id()
                virtual_activity._onchange_activity_type_id()
                next_activities_values.append(virtual_activity._convert_to_write(virtual_activity._cache))

            # post message on activity, before deleting it
            record = self.env[activity.res_model].browse(activity.res_id)
            record.message_post_with_view(
                'mail.message_activity_done',
                values={
                    'activity': activity,
                    'feedback': feedback,
                    'display_assignee': activity.user_id != self.env.user
                },
                subtype_id=self.env['ir.model.data']._xmlid_to_res_id('mail.mt_activities'),
                mail_activity_type_id=activity.activity_type_id.id,
                attachment_ids=[(4, attachment_id) for attachment_id in attachment_ids] if attachment_ids else [],
            )

            # Moving the attachments in the message
            # directly, see route /web_editor/attachment/add
            activity_message = record.message_ids[0]
            message_attachments = self.env['ir.attachment'].browse(activity_attachments[activity.id])
            if message_attachments:
                message_attachments.write({
                    'res_id': activity_message.id,
                    'res_model': activity_message._name,
                })
                activity_message.attachment_ids = message_attachments
            messages |= activity_message

        next_activities = self.env['mail.activity'].create(next_activities_values)
        self.update_activity()
        self.unlink()  # will unlink activity, dont access `self` after that

        return messages, next_activities

    def update_activity(self):
        '''
        THis will over ride built in feedback method
        :param feedback:
        :return:
        '''
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri = '{domain}activities/{id}'.format(domain=domain, id=self.pd_activity_id)
        uri_caller = uri
        _logger.info("******URI CALLER********* {}".format(uri_caller))
        company_id = self.env['res.users'].sudo().browse(self.env.user.id).company_id
        headers = {}
        payload = {
            'id': self.pd_activity_id,
            'done': 1
        }
        headers['Authorization'] = "Bearer " + company_id.access_token
        if company_id.access_token:
            _logger.info("Access token Found")
        else:
            raise UserError(_("Access Token not found!!!"))

        headers['content-type'] = 'application/x-www-form-urlencoded'
        response = requests.put(url=uri_caller, data=payload, headers=headers, verify=False)
        data = response.json()
        _logger.info("**************2 {}".format(data))
