odoo.define('debt.show_call', function(require) {
    'use strict';
    // alert("buttun")
    var WorkEntryControllerMixin = require('attendance.Late');
    var work_enty_default_js = require('hr_work_entry_contract_enterprise.work_entries_gantt')
    var GanttView = require('web_gantt.GanttView');
    var GanttController = require('web_gantt.GanttController');
    var viewRegistry = require('web.view_registry');

    var ListController = require('web.ListController');

    var WorkEntryGanttController = ListController.extend({
        events: _.extend({}, GanttController.prototype.events),


        _renderButtonsQWeb: function() {
            return this._super.apply(this, arguments).append(this._renderRegenerateLateButton());
        },
        _fetchRecords: function () {
            return this.model.ganttData.records;
        },
        _fetchFirstDay: function () {
            return this.model.ganttData.startDate;
        },
        _fetchLastDay: function () {
            return this.model.ganttData.stopDate;
        },
        _displayWarning: function ($warning) {
            this.$('.o_gantt_view').before($warning);
        },
    });

    var WorkEntryGanttView = GanttView.extend({
        config: _.extend({}, GanttView.prototype.config, {
            Controller: WorkEntryGanttController

        }),
    });

    viewRegistry.add('action_call', WorkEntryGanttView);

    return WorkEntryGanttController;

});
