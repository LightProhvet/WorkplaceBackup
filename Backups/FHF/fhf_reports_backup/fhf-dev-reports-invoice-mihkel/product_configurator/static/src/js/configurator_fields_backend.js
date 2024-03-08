odoo.define('product_configurator.configurator_fields_backend', function (require) {

// [UPDATED] now also allows configuring products on sale order.

"use strict";
var FieldOne2Many = require('web.relational_fields').FieldOne2Many;
var fieldRegistry = require('web.field_registry');
var ListRenderer = require('web.ListRenderer');
var ConfiguratorRenderer = ListRenderer.extend({

    _renderBodyCell: function (record, node, index, options) {
        var $cell = this._super.apply(this, arguments);

        if (node.attrs.name === "products"){
            if (record.data.line_config === "line_config_product"){
                if (record.data.hidden_status){
                    return $cell.addClass('o_hidden');
                }
                if (record.data.readonly_status){
                    return $cell;
                }
                return $cell;
            }
            else{
                return $cell.addClass('o_hidden');
            }
        }

        else if (node.attrs.name === "float_values") {
            if (record.data.line_config === "line_config_float") {
                if (record.data.hidden_status){
                    return $cell.addClass('o_hidden');
                }
                if (record.data.readonly_status){
                    return $cell;
                }
                return $cell;
            }
            else {
                return $cell.addClass('o_hidden');
            }
        }
        else if (node.attrs.name === "text_value") {;
            if (record.data.line_config === "line_config_text") {
                if (record.data.hidden_status){
                    return $cell.addClass('o_hidden');
                }
                if (record.data.readonly_status){
                    return $cell;
                }
                return $cell;
            }
            else {
                return $cell.addClass('o_hidden');
            }
        }
        else if (node.attrs.name === "type_list") {
            if (record.data.line_config === "line_config_type") {
                if (record.data.hidden_status){
                    return $cell.addClass('o_hidden');
                }
                if (record.data.readonly_status){
                    return $cell;
                }
                return $cell;
            }
            else {
                return $cell.addClass('o_hidden');
            }
        }
        else if (node.attrs.name === "template_check") {
            if (record.data.line_config === "line_config_template") {
                if (record.data.hidden_status){
                    return $cell.addClass('o_hidden');
                }
                if (record.data.readonly_status){
                    return $cell;
                }
                return $cell;
            }
            else {
                return $cell.addClass('o_hidden');
            }
        }
        return $cell;
    },

    _renderRow: function (record, index) {
        var $row = this._super.apply(this, arguments);
        if (record.data.display_type) {
            $row.addClass('o_is_' + record.data.display_type);
        }
        return $row;
    },

    _renderView: function () {
        var def = this._super();
        this.$el.find('> table').addClass('o_configurator_list_view');
        return def;
    },
 });

var ConfiguratorFieldOne2Many = FieldOne2Many.extend({
    _getRenderer: function () {
        if (this.view.arch.tag === 'tree') {
            return ConfiguratorRenderer;
        }
        return this._super.apply(this, arguments);
    },
});

fieldRegistry.add('configurator_one2many', ConfiguratorFieldOne2Many);
});