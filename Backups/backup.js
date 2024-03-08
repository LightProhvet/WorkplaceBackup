/** @odoo-module **/

var FieldMany2One = require('web.relational_fields').FieldMany2One;

console.log("Test run on backup");

FieldMany2One.include({
/**
     * override to trigger search more always
     *
     * @private
     * @override
     */
     _search: async function (searchValue = "") {
        console.log(" running INSIDE on search_more");
        console.log(this.field.relation);
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
        if (1 < values.length && this.field.relation == 'product.custom.configurator.instance') {
            values = this._manageSearchMore(values, value, domain, context);
        } else if (this.limit < values.length) {
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
    }
});

export default FieldMany2One;

