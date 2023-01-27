# -*- coding: utf-8 -*-
import base64
import logging
import os
from datetime import datetime
from io import BytesIO

import pytz

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class SFTPModelTemplate(models.Model):
    _name = 'sftp.export.template'
    _description = 'SFTP Export Template'

    connector_id = fields.Many2one('sftp.connection', string='SFTP Connection')
    name = fields.Char(string="Name")
    path = fields.Char(string="SFTP Destination Path",
                       help='Enter Sftp Folder Name here')
    model_name = fields.Many2one('ir.model', string="Model Name")
    # model_domain = fields.Char(related='model_name.model', string="Model Domain")
    # domain_set = fields.Char()
    cron_id = fields.Many2one('ir.cron', string='Schedule Action')
    interval_number = fields.Integer(default="1")
    interval_type = fields.Selection(string='Interval Type',
                                     selection=[('minutes', 'Minutes'),
                                                ('hours', 'Hours'),
                                                ('days', 'Days'),
                                                ('weeks', 'Weeks'),
                                                ('months', 'Months'), ],
                                     default="days")
    run_date = fields.Datetime(string='Run Date')
    cron_active = fields.Boolean(string="Active", default=True)
    log_book_id = fields.One2many('log.book', 'template_id', string="Log Book")

    @api.model
    def create(self, vals):
        res = super(SFTPModelTemplate, self).create(vals)
        code = 'model.cron_sftp_update(' + str(res.id) + ')'
        model_id = self.env['ir.model'].search(
            [('model', '=', 'sftp.export.template')]).id
        cron_data = {
            'name': res.name or False,
            'interval_number': res.interval_number or False,
            'interval_type': res.interval_type,
            'numbercall': -1,
            'code': code,
            'model_id': self._context.get('use_model', model_id),
            'state': 'code'
        }
        cron = self.env['ir.cron'].sudo().create(cron_data)
        res.cron_id = cron.id
        return res

    @api.onchange('interval_number', 'interval_type', 'run_date', 'cron_active', 'name')
    def run_schedule_activity(self):
        if self.cron_id:
            values = {
                'active': self.cron_active
            }
            if self.interval_number:
                values['interval_number'] = self.interval_number
            if self.interval_type:
                values['interval_type'] = self.interval_type
            if self.run_date:
                values['nextcall'] = self.run_date
            if self.name:
                values['name'] = self.name

            self.cron_id.sudo().write(values)

    def export_data(self):
        if self.connector_id:
            user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
            today = datetime.now(user_tz)

            # Set the start and end of the day in UTC
            start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = today.replace(hour=23, minute=59, second=59, microsecond=999999)

            domain = [('state', '=', 'posted'), ('create_date', '>=', start_of_day.strftime('%Y-%m-%d %H:%M:%S')),
                      ('create_date', '<', end_of_day.strftime('%Y-%m-%d %H:%M:%S'))]
            records = self.env[self.model_name.model].search(domain)
            attachments = []
            for record in records:
                if 'message_main_attachment_id' in record._fields:
                    if not record.message_main_attachment_id:
                        # if self.model_name.model == 'account.move':
                        pdf = self.env.ref('account.account_invoices').sudo()._render_qweb_pdf(
                            [record.id])[0]
                        # elif self.model_name.model == 'sale.order':
                        #     pdf = self.env.ref('sale.action_report_saleorder').sudo()._render_qweb_pdf(
                        #         [record.id])[0]
                        pdf = base64.b64encode(pdf)
                        binary_data = pdf
                    else:
                        binary_data = record.message_main_attachment_id.datas

                    filename = record.message_main_attachment_id.name

                    remote_path = os.path.join(self.path, filename)

                    base64_file = base64.b64decode(binary_data)
                    pdf_file = BytesIO(base64_file)
                    status = self.connector_id.send_file(pdf_file, remote_path)
                    if status:
                        attachments.append((4, record.message_main_attachment_id.id))
                        record.invoice_sent = True
                        record.message_main_attachment_id.file_sent = True
                    else:
                        record.invoice_sent = True
                        record.message_main_attachment_id.file_sent = False
            state = False
            if any(not rec.message_main_attachment_id.file_sent for rec in records):
                state = 'partial'
            if all(not rec.message_main_attachment_id.file_sent for rec in records):
                state = 'fail'
            if all(rec.message_main_attachment_id.file_sent for rec in records):
                state = 'done'

            log_book_vals = {
                'name': 'Book_'+start_of_day.strftime('%Y_%m_%d'),
                'state': state,
                'template_id': self.id,
                'date': fields.datetime.now(),
                'attachment_ids': attachments,
            }
            self.env['log.book'].sudo().create(log_book_vals)

    def cron_sftp_update(self, rec_id):
        export_id = self.search([('id', '=', int(rec_id))])
        if export_id:
            export_id.export_data()


class LogBook(models.Model):
    _name = 'log.book'
    _description = "Log Book"

    name = fields.Char(string="Name")
    template_id = fields.Many2one('sftp.export.template', string="Template")
    # log_book_lines = fields.One2many('log.book.line', 'log_book_id', string="Log Book Lines")
    date = fields.Datetime(string='Synced Date')
    attachment_ids = fields.Many2many('ir.attachment', string='Synced Attachments')
    state = fields.Selection(string='Status',
                             selection=[('done', 'Done'),
                                        ('fail', 'Failed'),
                                        ('partial', 'Partial'),
                                        ])


# class LogBookLine(models.Model):
#     _name = 'log.book.line'
#     _description = "Log Book"
#
#     name = fields.Char(string="Name")
#     log_book_id = fields.Many2one('sftp.export.template', string="Log Book")
#     state = fields.Selection(string='Status',
#                              selection=[('success', 'Success'),
#                                         ('fail', 'Failed'),
#                                         ])