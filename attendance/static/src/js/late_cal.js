odoo.define('attendance.work_entries_cal', function (require) {
    'use strict';

    var WorkEntryPayrollHolidaysControllerMixin = require('attendance.Late');
    var WorkEntryGanttController = require("hr_work_entry_contract_enterprise.work_entries_gantt");

    var WorkEntryPayrollHolidaysGanttController = WorkEntryGanttController.include(WorkEntryPayrollHolidaysControllerMixin);

    return WorkEntryPayrollHolidaysGanttController;

});
