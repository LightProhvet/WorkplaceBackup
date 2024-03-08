/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ListRenderer } from "@web/views/list/list_renderer";
import { X2ManyField } from "@web/views/fields/x2many/x2many_field";

console.log("Test run...");
const { Component, useEffect } = owl;

export class ConfiguratorListRenderer extends ListRenderer {
    /**
     * The purpose of this extension is to allow sections and notes in the one2many list
     * primarily used on Sales Orders and Invoices
     *
     * @override
     */
    setup() {
        super.setup();
        this.titleField = "name";
        useEffect(
            () => this.focusToName(this.props.list.editedRecord),
            () => [this.props.list.editedRecord]
        )
    }

    focusToName(editRec) {
        if (editRec && editRec.isVirtual && this.isSectionOrNote(editRec)) {
            const col = this.state.columns.find((c) => c.name === this.titleField);
            this.focusCell(col, null);
        }
    }

    isSectionOrNote(record=null) {
        record = record || this.record;
        return ['line_section', 'line_note'].includes(record.data.display_type);
    }

    getCellClass(column, record) {
        const classNames = super.getCellClass(column, record);
        if (column.name === "products"){
            if (record.data.line_config === "line_config_product"){
                if (record.data.hidden_status){
                    return `${classNames} o_hidden`;
                }
                if (record.data.readonly_status){
                    return classNames;
                }
                return classNames;
            }
            else{
                return `${classNames} o_hidden`;
            }
        }
        if (column.name === "float_values"){
            if (record.data.line_config === "line_config_float"){
                if (record.data.hidden_status){
                    return `${classNames} o_hidden`;
                }
                if (record.data.readonly_status){
                    return classNames;
                }
                return classNames;
            }
            else{
                return `${classNames} o_hidden`;
            }
        }
        if (column.name === "text_value"){
            if (record.data.line_config === "line_config_text"){
                if (record.data.hidden_status){
                    return `${classNames} o_hidden`;
                }
                if (record.data.readonly_status){
                    return classNames;
                }
                return classNames;
            }
            else{
                return `${classNames} o_hidden`;
            }
        }
        if (column.name === "type_list"){
            if (record.data.line_config === "line_config_type"){
                if (record.data.hidden_status){
                    return `${classNames} o_hidden`;
                }
                if (record.data.readonly_status){
                    return classNames;
                }
                return classNames;
            }
            else{
                return `${classNames} o_hidden`;
            }
        }
        if (column.name === "template_check"){
            if (record.data.line_config === "line_config_template"){
                if (record.data.hidden_status){
                    return `${classNames} o_hidden`;
                }
                if (record.data.readonly_status){
                    return classNames;
                }
                return classNames;
            }
            else{
                return `${classNames} o_hidden`;
            }
        }
        return classNames;
    }
}
ConfiguratorListRenderer.template = "product_configurator.configuratorListRenderer";

export class ConfiguratorFieldOne2Many extends X2ManyField {}
ConfiguratorFieldOne2Many.components = {
    ...X2ManyField.components,
    ListRenderer: ConfiguratorListRenderer,
};


registry.category("fields").add("configurator_one2many", ConfiguratorFieldOne2Many);
