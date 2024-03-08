/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ListRenderer } from "@web/views/list/list_renderer";
import { X2ManyField } from "@web/views/fields/x2many/x2many_field";

console.log("Test run...");
const { Component, useEffect } = owl;

export class ConfiguratorInputListRenderer extends ListRenderer {
    /**
     * The purpose of this extension is to display only existing columns in line.
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
       //props: "activeActions?",
//    "list",
//    "archInfo",
//    "openRecord",
//    "onAdd?",
//    "cycleOnTab?",
//    "allowSelectors?",
//    "editable?",
//    "noContentHelp?",
//    "nestedKeyOptionalFieldsData?",
//    "readonly?",

       // juba on olemas: Getterid:  isEmpty(), fields(), getOptionalFields, displayOptionalFields, selectAll, getColumnClass, getColumns, canSelectRecord
       // functions: onCellClicked, onButtonCellClicked, isInlineEditable, findNextFocusableOnRow, toggleSelection, toggleOptionalField, onGlobalClick(ev), sortDrop, sortStart

    //TODO: change to getCellvalue - check whether cell has value
    getCellvalue(column, record) {

    }
//    getCellClass(column, record) {
//        const classNames = super.getCellClass(column, record);
//        if (column.name === "products"){
//            if (record.data.line_config === "line_config_product"){
//                if (record.data.hidden_status){
//                    return `${classNames} o_hidden`;
//                }
//                if (record.data.readonly_status){
//                    return classNames;
//                }
//                return classNames;
//            }
//            else{
//                return `${classNames} o_hidden`;
//            }
//        }
//        if (column.name === "float_values"){
//            if (record.data.line_config === "line_config_float"){
//                if (record.data.hidden_status){
//                    return `${classNames} o_hidden`;
//                }
//                if (record.data.readonly_status){
//                    return classNames;
//                }
//                return classNames;
//            }
//            else{
//                return `${classNames} o_hidden`;
//            }
//        }
//        if (column.name === "text_value"){
//            if (record.data.line_config === "line_config_text"){
//                if (record.data.hidden_status){
//                    return `${classNames} o_hidden`;
//                }
//                if (record.data.readonly_status){
//                    return classNames;
//                }
//                return classNames;
//            }
//            else{
//                return `${classNames} o_hidden`;
//            }
//        }
//        if (column.name === "type_list"){
//            if (record.data.line_config === "line_config_type"){
//                if (record.data.hidden_status){
//                    return `${classNames} o_hidden`;
//                }
//                if (record.data.readonly_status){
//                    return classNames;
//                }
//                return classNames;
//            }
//            else{
//                return `${classNames} o_hidden`;
//            }
//        }
//        if (column.name === "template_check"){
//            if (record.data.line_config === "line_config_template"){
//                if (record.data.hidden_status){
//                    return `${classNames} o_hidden`;
//                }
//                if (record.data.readonly_status){
//                    return classNames;
//                }
//                return classNames;
//            }
//            else{
//                return `${classNames} o_hidden`;
//            }
//        }
//        return classNames;
//    }
}
ConfiguratorInputListRenderer.template = "product_configurator.configuratorInputListRenderer";

export class ConfiguratorInputFieldOne2Many extends X2ManyField {}
ConfiguratorInputFieldOne2Many.components = {
    ...X2ManyField.components,
    ListRenderer: ConfiguratorInputListRenderer,
};


registry.category("fields").add("configurator_one2many", ConfiguratorInputFieldOne2Many);
