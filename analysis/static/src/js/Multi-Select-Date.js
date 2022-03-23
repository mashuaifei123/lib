odoo.define('date_auto-kal', function (require) {
    "use strict";
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;
    var _lt = core._lt;
    var AbstractField = require('web.AbstractField');
    var InputField = require('web.basic_fields').InputField;
    var fieldRegistry = require('web.field_registry');

    var MultiSelectDateField = InputField.extend({
        jsLibs: [
            '/project_bom/static/src/js/kalendae.standalone.js',
        ],
        cssLibs: [
            '/project_bom/static/src/css/kalendae.css',
        ],
        init: function () {
            this._super.apply(this, arguments);
        },
        _renderEdit: function () {
            this._super.apply(this, arguments);
            var self = this;
            this.$el.kalendae({format:'YYYY-MM-DD',months:2,mode:'multiple',dayHeaderClickable:true,});
        }
    });

    fieldRegistry.add('Multi-Select-Date', MultiSelectDateField);

    return {
        MultiSelectDateField: MultiSelectDateField,
    };
});
