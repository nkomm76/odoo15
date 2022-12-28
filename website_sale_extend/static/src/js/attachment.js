odoo.define('website_sale_extend.checkout_form', function (require) {
'use strict';

var website_sale = require('payment.checkout_form');
var publicWidget = require('web.public.widget');
const wUtils = require('website.utils');

publicWidget.registry.PaymentCheckoutForm.include({

    /**
     * Open a modal if attachments are not uploaded
     * @override
     */
    _onClickPay: async function (ev) {
        ev.stopPropagation();
        ev.preventDefault();

        var $attachments = $('input[name="attachment_count"]');
        if (parseInt($attachments.val()) === 0){
            $('#sale_attachment_warning').modal('show');
        }else{
            return this._super(...arguments);
        }
    },
});

});

const btn = document.getElementById('add_attachment');
if(btn){
    btn.addEventListener('click', () => {
      $('#add_sale_attachment').modal('hide');
    });
}

