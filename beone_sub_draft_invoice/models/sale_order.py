# -*- coding: utf-8 -*-

import logging

from odoo.addons.sale_subscription.models.sale_order import SaleOrder

_logger = logging.getLogger(__name__)


def _new_handle_automatic_invoices(self, auto_commit, invoices):
    """ This method handle the subscription with or without payment token """
    Mail = self.env['mail.mail']
    automatic_values = self._get_automatic_subscription_values()
    existing_invoices = invoices
    for order in self:
        invoice = invoices.filtered(lambda inv: inv.invoice_origin == order.name)
        email_context = self._get_subscription_mail_payment_context()
        # Set the contract in exception. If something go wrong, the exception remains.
        order.with_context(mail_notrack=True).write({'payment_exception': True})
        if not order.payment_token_id:
            # BEONE edited : handle the draft invoicing
            if order.recurrence_id.draft_invoice:
                self.env.cr.commit()
            else:
                invoice.action_post()
        else:
            payment_callback_done = False
            try:
                payment_token = order.payment_token_id
                transaction = None
                # execute payment
                if payment_token:
                    if not payment_token.partner_id.country_id:
                        msg_body = 'Automatic payment failed. Contract set to "To Renew". No country specified on payment_token\'s partner'
                        order.message_post(body=msg_body)
                        order.with_context(mail_notrack=True).write(automatic_values)
                        invoice.unlink()
                        existing_invoices -= invoice
                        if auto_commit:
                            self.env.cr.commit()
                        continue
                    transaction = order._do_payment(payment_token, invoice)
                    payment_callback_done = transaction and transaction.sudo().callback_is_done
                    # commit change as soon as we try the payment, so we have a trace in the payment_transaction table
                    if auto_commit:
                        self.env.cr.commit()
                # if transaction is a success, post a message
                if transaction and transaction.state == 'done':
                    order.with_context(mail_notrack=True).write({'payment_exception': False})
                    self._subscription_post_success_payment(invoice, transaction)
                    if auto_commit:
                        self.env.cr.commit()
                # if no transaction or failure, log error, rollback and remove invoice
                if transaction and not transaction.renewal_allowed:
                    if auto_commit:
                        # prevent rollback during tests
                        self.env.cr.rollback()
                    order._handle_subscription_payment_failure(invoice, transaction, email_context)
                    existing_invoices -= invoice  # It will be unlinked in the call above
            except Exception:
                if auto_commit:
                    # prevent rollback during tests
                    self.env.cr.rollback()
                # we suppose that the payment is run only once a day
                last_transaction = self.env['payment.transaction'].search(['|',
                                                                           (
                                                                               'reference', 'like',
                                                                               order.client_order_ref),
                                                                           ('reference', 'like', order.name)
                                                                           ], limit=1)
                error_message = "Error during renewal of contract [%s] %s (%s)" \
                                % (order.id, order.client_order_ref or order.name,
                                   'Payment recorded: %s' % last_transaction.reference
                                   if last_transaction and last_transaction.state == 'done' else 'Payment not recorded')
                _logger.exception(error_message)
                mail = Mail.sudo().create({'body_html': error_message, 'subject': error_message,
                                           'email_to': email_context.get('responsible_email'), 'auto_delete': True})
                mail.send()
                if invoice.state == 'draft':
                    existing_invoices -= invoice
                    if not payment_callback_done:
                        invoice.unlink()

    return existing_invoices


SaleOrder._handle_automatic_invoices = _new_handle_automatic_invoices
