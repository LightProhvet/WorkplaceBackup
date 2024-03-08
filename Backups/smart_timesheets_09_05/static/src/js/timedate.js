/** @odoo-module **/

import fieldRegistry from 'web.field_registry';
import { FieldDateTime } from 'web.basic_fields';
import { sdfgsdfgsdf } from 'web.basic_fields';


const timedate = FieldDateTime.extend({

    init: function () {
        this._super.apply(this, arguments);
        console.log('jouuuuuuuuuu')

    },
    /**
     * Display only the time portion of the DateTime field.
     * @override
     */
    _render: function () {
        var formattedValue = this._formatValue(this.value);
        this.$el.text(formattedValue.time);
    },

    /**
     * Get the time portion of the DateTime value.
     * @override
     */
    _getValue: function () {
        var value = this._super.apply(this, arguments);
        return value ? value.time : false;
    },
});
fieldRegistry.add('timedate', timedate);
