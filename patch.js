/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import KioskMode from "@hr_attendance/js/kiosk_mode";

console.log("Fail loaded!")
patch(KioskMode.prototype, 'kiosk_mode', {
    /**
     * @override
     */
    start: function () {
        var self = this;
        core.bus.on('barcode_scanned', this, this._onBarcodeScanned);
        self.session = Session;
        const company_id = this.session.user_context.allowed_company_ids[0];
        console.log("Good job!")
        var def = this._rpc({
                model: 'res.company',
                method: 'search_read',
                args: [[['id', '=', company_id]], ['name', 'attendance_kiosk_mode', 'attendance_barcode_source']],
            })
            .then(function (companies){
                self.company_name = companies[0].name;
                self.company_image_url = self.session.url('/web/image', {model: 'res.company', id: company_id, field: 'logo',});
                self.kiosk_mode = companies[0].attendance_kiosk_mode;
                self.barcode_source = companies[0].attendance_barcode_source;
//                self.$el.html(QWeb.render("HrAttendanceKioskMode", {widget: self}));
// Do not render the kiosk mode, rather open the kanban
                this.do_action('hr_attendance.hr_employee_attendance_action_kanban', {
                                additional_context: {'no_group_by': true},
                            });
                self.start_clock();
                });
            // Make a RPC call every day to keep the session alive
        self._interval = window.setInterval(this._callServer.bind(this), (60*60*1000*24));
        return Promise.all([def, this._super.apply(this, arguments)]);
        },
});
