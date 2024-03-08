odoo.define('pinska_product_configurator.search_more_limit', function (require) {
"use strict";

var config = require('web.config');
var core = require('web.core');
var relational_fields = require('web.relational_fields');

var FieldMany2One = relational_fields.FieldMany2One;
var FieldX2Many = relational_fields.FieldX2Many;
var qweb = core.qweb;

/**
 * Override the Many2One to have search more always available.
 */

FieldMany2One.include({
    /**
     * @override
     * @param {boolean} [options.noOpen=false] if true, there is no external
     *   button to open the related record in a dialog
     * @param {boolean} [options.noCreate=false] if true, the many2one does not
     *   allow to create records
     */
    init: function (parent, name, record, options) {
        options = options || {};
        this._super.apply(this, arguments);
        this.limit = 1;
        console.log("Test run on INIT, limited");

        this.orderer = new concurrency.DropMisordered();

        // should normally be set, except in standalone M20
        const canCreate = 'can_create' in this.attrs ? JSON.parse(this.attrs.can_create) : true;
        this.can_create = canCreate && !this.nodeOptions.no_create && !options.noCreate;
        this.can_write = 'can_write' in this.attrs ? JSON.parse(this.attrs.can_write) : true;

        this.nodeOptions = _.defaults(this.nodeOptions, {
            quick_create: true,
        });
        this.noOpen = 'noOpen' in options ? options.noOpen : this.nodeOptions.no_open;
        this.m2o_value = this._formatValue(this.value);
        // 'recordParams' is a dict of params used when calling functions
        // 'getDomain' and 'getContext' on this.record
        this.recordParams = {fieldName: this.name, viewType: this.viewType};
        // We need to know if the widget is dirty (i.e. if the user has changed
        // the value, and those changes haven't been acknowledged yet by the
        // environment), to prevent erasing that new value on a reset (e.g.
        // coming by an onchange on another field)
        this.isDirty = false;
        this.lastChangeEvent = undefined;

        // List of autocomplete sources
        this._autocompleteSources = [];
        // Add default search method for M20 (name_search)
        this._addAutocompleteSource(this._search, {placeholder: _t('Loading...'), order: 1});

        // list of last autocomplete suggestions
        this.suggestions = [];

        // flag used to prevent from selecting the highlighted item in the autocomplete
        // dropdown when the user leaves the many2one by pressing Tab (unless he
        // manually selected the item using UP/DOWN keys)
        this.ignoreTabSelect = false;

        // use a DropPrevious to properly handle related record quick creations,
        // and store a createDef to be able to notify the environment that there
        // is pending quick create operation
        this.dp = new concurrency.DropPrevious();
        this.createDef = undefined;
    },
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------
/**
     * Executes a 'name_search' and returns a list of formatted objects meant to
     * be displayed in the autocomplete widget dropdown. These items are either:
     * - a formatted version of a 'name_search' result
     * - an option meant to display additional information or perform an action
     *
     * @private
     * @param {string} [searchValue=""]
     * @returns {Promise<{
     *      label: string,
     *      id?: number,
     *      name?: string,
     *      value?: string,
     *      classname?: string,
     *      action?: () => Promise<any>,
     * }[]>}
     */
    _search: async function (searchValue = "") {
        console.log("Test run inside the search");
        const value = searchValue.trim();
        const domain = this.record.getDomain(this.recordParams);
        const context = Object.assign(
            this.record.getContext(this.recordParams),
            this.additionalContext
        );

        // Exclude black-listed ids from the domain
        const blackListedIds = this._getSearchBlacklist();
        if (blackListedIds.length) {
            domain.push(['id', 'not in', blackListedIds]);
        }

        if (this.lastNameSearch) {
            this.lastNameSearch.catch((reason) => {
                // the last rpc name_search will be aborted, so we want to ignore its rejection
                reason.event.preventDefault();
            })
            this.lastNameSearch.abort(false)
        }
        this.lastNameSearch = this._rpc({
            model: this.field.relation,
            method: "name_search",
            kwargs: {
                name: value,
                args: domain,
                operator: "ilike",
                limit: this.limit + 1,
                context,
            }
        });
        const results = await this.orderer.add(this.lastNameSearch);

        // Format results to fit the options dropdown
        let values = results.map((result) => {
            const [id, fullName] = result;
            const displayName = this._getDisplayName(fullName).trim();
            result[1] = displayName;
            return {
                id,
                label: escape(displayName) || data.noDisplayContent,
                value: displayName,
                name: displayName,
            };
        });

        // Add "Search more..." option if results count is higher than the limit
        if (1 < values.length) {
            values = this._manageSearchMore(values, value, domain, context);
        }

        // Additional options...
        const canQuickCreate = this.can_create && !this.nodeOptions.no_quick_create;
        const canCreateEdit = this.can_create && !this.nodeOptions.no_create_edit;
        if (value.length) {
            // "Quick create" option
            const nameExists = results.some((result) => result[1] === value);
            if (canQuickCreate && !nameExists) {
                values.push({
                    label: sprintf(
                        _t(`Create "<strong>%s</strong>"`),
                        escape(value)
                    ),
                    action: () => this._quickCreate(value),
                    classname: 'o_m2o_dropdown_option'
                });
            }
            // "Create and Edit" option
            if (canCreateEdit) {
                const valueContext = this._createContext(value);
                values.push({
                    label: _t("Create and Edit..."),
                    action: () => {
                        // Input value is cleared and the form popup opens
                        this.el.querySelector(':scope input').value = "";
                        return this._searchCreatePopup('form', false, valueContext);
                    },
                    classname: 'o_m2o_dropdown_option',
                });
            }
            // "No results" option
            if (!values.length) {
                values.push({
                    label: _t("No records"),
                    classname: 'o_m2o_no_result',
                });
            }
        } else if (!this.value && (canQuickCreate || canCreateEdit)) {
            // "Start typing" option
            values.push({
                label: _t("Start typing..."),
                classname: 'o_m2o_start_typing',
            });
        }

        return values;
    },
    /**
     * We always open Many2One search dialog for select/update field value
     * instead of autocomplete
     *
     * @private
     * @override
     */
    _toggleAutoComplete: function () {
        console.log("Test run on INIT, limited, autocomplete");
        this._searchCreatePopup("search");
    },
});
console.log("Test run on backup, i tried");
});
