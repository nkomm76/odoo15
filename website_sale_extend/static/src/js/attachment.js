odoo.define('website_sale_extend.website_sale_attachments', function (require) {
'use strict';

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

    publicWidget.registry.websiteOrderAttachments = publicWidget.Widget.extend({
        selector: '.oe_website_sale',
        events: {
            'click .js_delete_attachment': '_onClickDeleteAttachment',
        },

        _onClickDeleteAttachment: async function (ev){
            ev.preventDefault();
            var attachment_id = ev.currentTarget.getAttribute('data');
            this._rpc({
                route: "/shop/attachment/delete",
                params: {
                    attachment_id: attachment_id,
                },
            }).then(function (data) {
                if (data){
                    $(ev.currentTarget).closest('div').find('input[name="attachment_count"]').val(data.attachment_count)
                    if (data.removed && data.attachment_count === 0){
                        $(ev.currentTarget).closest('table').remove()
                    }else{
                        $(ev.currentTarget).closest('tr').remove()
                    }
                }
            });
        },
    });
    return publicWidget.registry.websiteOrderAttachments
});

odoo.define('website_sale_extend.website_order_attachment_popup', function (require) {
'use strict';

    var publicWidget = require('web.public.widget');
    const wUtils = require('website.utils');
    publicWidget.registry.websiteOrderAttachmentsPopup = publicWidget.Widget.extend({
        selector: '.attachment_modal_form',
        events: {
            'click #add_attachment': '_onClickAddAttachment',
        },

        _onClickAddAttachment: async function (ev){
            var types = ['image/jpg', 'image/jpeg', 'image/png' ,'application/pdf']
            var $uploadedFiles = $('#attachments').prop('files')
            for (const file of $uploadedFiles) {
                if (types.includes(file.type) === false){
                    $('#attachment_extension_warning').modal('show');
                    ev.stopPropagation();
                    ev.preventDefault();
                }else{
                    $('#add_sale_attachment').modal('hide');
                }
              }

        },
    });
    return publicWidget.registry.websiteOrderAttachmentsPopup
});

