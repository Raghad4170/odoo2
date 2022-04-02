odoo.define('attendance.work_entries_gantt', function (require) {
    'use strict';

    // alert("mmmmmmmmmmm")
    var WorkEntryPayrollControllerMixin = require('attendance.Late');
    var WorkEntryGanttController = require("hr_work_entry_contract_enterprise.work_entries_gantt");

    var WorkEntryPayrollGanttController = WorkEntryGanttController.include(WorkEntryPayrollControllerMixin);

    return WorkEntryPayrollGanttController;

});
