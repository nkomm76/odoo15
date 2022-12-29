odoo.define('website_sale_extend.website_sale_attachments', function (require) {
'use strict';

    var publicWidget = require('web.public.widget');
    const wUtils = require('website.utils');
    var WebsiteSale = require('website_sale.website_sale');

    publicWidget.registry.WebsiteSale.include({

        events: _.extend({}, WebsiteSale.events, {
            'click .js_delete_attachment': '_onClickDeleteAttachment',
        }),

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
                        debugger
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
            $('#add_sale_attachment').modal('hide');
        },
    });
    return publicWidget.registry.websiteOrderAttachmentsPopup
});

