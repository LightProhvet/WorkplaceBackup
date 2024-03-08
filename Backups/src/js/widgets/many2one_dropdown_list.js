//zodoo.define('web.relational_fields', function (require) {
//"use strict";
//
//
//var ListRenderer = require('web.ListRenderer');
//const { ComponentWrapper, WidgetAdapterMixin } = require('web.OwlCompatibility');
///**
// * Widget Many2OneAvatar is only supported on many2one fields pointing to a
// * model which inherits from 'image.mixin'. In readonly, it displays the
// * record's image next to the display_name. In edit, it behaves exactly like a
// * regular many2one widget.
// */
//const Many2OneAvatar = FieldMany2One.extend({
//    _template: 'web.Many2One',
//
//    init() {
//        this._super.apply(this, arguments);
//        if (this.mode === 'readonly') {
//            this.template = null;
//            this.tagName = 'div';
//            // disable the redirection to the related record on click, in readonly
//            this.noOpen = true;
//        }
//    },
//    start() {
//        this.el.classList.add('o_field_many2one_avatar');
//        return this._super(...arguments);
//    },
//
//    //--------------------------------------------------------------------------
//    // Private
//    //--------------------------------------------------------------------------
//
//    /**
//     * Adds avatar image to before many2one value.
//     *
//     * @override
//     */
//    _render() {
//        const m2oAvatar = qweb.render(this._template, {
//            url: `/web/image/${this.field.relation}/${this.value.res_id}/avatar_128`,
//            value: this.m2o_value,
//            widget: this,
//        });
//        if (this.mode === 'edit') {
//            this._super(...arguments);
//            if (this.el.querySelector('.o_m2o_avatar')) {
//                this.el.querySelector('.o_m2o_avatar').remove();
//            }
//            dom.prepend(this.$('.o_field_many2one_selection'), m2oAvatar);
//        }
//        if (this.mode === 'readonly') {
//            this.$el.empty();
//            dom.append(this.$el, m2oAvatar);
//        }
//    },
//});
