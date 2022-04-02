// Copyright to The City Law Firm
odoo.define('attendance.Late', function(require) {
    'use strict';
    // alert('I am In')
    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;
    var time = require('web.time');
    //alert("ffffffff")

    
    var Late = {


       /**
         * @override
         * @returns {Promise}
         */
        _update: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.firstDay = self._fetchFirstDay().toDate();
                self.lastDay = self._fetchLastDay().toDate();
                var now = moment();
                if (self.firstDay > now) return Promise.resolve();
                // return self._renderRegenerateLateButton();
            });
        },

        updateButtons: function() {
            this._super.apply(this, arguments);

            if(!this.$buttons) {
                //alert("ppppppppppp")
                return;
            }

            this.$buttons.find('.btn-regenerate-work-entriess').on('click', this._onRegenerateLates.bind(this));
        },

        renderButtons: function($node) {
            this._super.apply(this, arguments);

            if(this.$buttons) {
                //alert("yeeeeeeeeeeeeeeeeee")
                this.$buttons.append(this._renderRegenerateLateButton());
                
            }
        },

        /*
            Private
        */
       _renderRegenerateLateButton: function() {
           //alert("hello")
            return $('<span>').append(QWeb.render('late_work_entry_button', {
                button_text: _t("إنشاء الغياب من برنامج الحضور"),
                event_class: 'btn-regenerate-work-entriess',
            }));
        },

        _renderRegenerateLateButtonfun: function () {
            var self = this;
            return this._rpc({
                model: 'hr.employee',
                method: 'generate_work_entries',
                args: [[], time.date_to_str(this.firstDay), time.date_to_str(this.lastDay)],
            }).then(function (new_work_entries) {
                if (new_work_entries) {
                    self.reload();
                }
            });
        },

        _regenerateLatees: function () {
            this.do_action('attendance.late_regeneration_wizard_action', {
                additional_context: {
                    date_start: time.date_to_str(this.firstDay),
                    date_end: time.date_to_str(this.lastDay),
                },
            });
        },

        _onRegenerateLates: function (e) {
            e.preventDefault();
            e.stopImmediatePropagation();
            this._regenerateLatees();
        },


    };

    return Late;


    var WorkEntryGanttController = require("hr_payroll.work_entries_gantt");

    var WorkEntryPayrollGanttController = WorkEntryGanttController.include(Late);

    // var WorkEntryCalendarController = require("hr_payroll.work_entries_calendar");

    // WorkEntryCalendarController.include(Late);

    return WorkEntryPayrollGanttController;
});
