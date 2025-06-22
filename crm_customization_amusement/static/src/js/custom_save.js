odoo.define('crm_customization_amusement.custom_save_button', function (require) {
    'use strict';

    var FormController = require('web.FormController');

    FormController.include({
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.find('.o_custom_save_btn').on('click', this._onCustomSave.bind(this));
            }
        },

        _onCustomSave: function () {
            // This triggers the actual save logic
            this.saveRecord();
        }
    });
});
