odoo.define('work_trip.work_trip', function (require) {
    "use strict";
    
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var field_utils = require('web.field_utils');
    
    
    var MyAttendances = AbstractAction.extend({
        contentTemplate: 'WorkTrip',
        events: {
            "click .o_travel_icon": _.debounce(function() {
                this.start_work_trip();
            }, 200, true),
            "click .o_travel_icon_end": _.debounce(function() {
                this.end_work_trip();
            }, 200, true),
        },
    
        willStart: function () {
            var self = this;
            // var $country = this.$('select[name="seasons"]');
            // alert($country.val())

            var def = this._rpc({
                    model: 'hr.employee',
                    method: 'search_read',
                    args: [[['user_id', '=', this.getSession().uid]], ['trip_state', 'name', 'hours_today']],
                })
                .then(function (res) {
                    self.employee = res.length && res[0];
                    // alert(self.employee)

                    if (res.length) {
                        self.hours_today = field_utils.format.float_time(self.employee.hours_today);
                    }
                });
    
            return Promise.all([def, this._super.apply(this, arguments)]);
        },
    
        start_work_trip: function () {
            var self = this;
            // var $country = this.$('select[name="seasons"]');
            // alert($country.val())
            // alert(this.$( ".reasons" ).val())

            this._rpc({
                    model: 'hr.employee',
                    method: 'update_work_trip',
                    args: [[self.employee.id],'start',this.$( ".reasons" ).val()]
                })
                .then(function(result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                    }
                });
                location.reload();

        },

        end_work_trip: function () {
            var self = this;
            // alert(this.$( ".reasons" ).val())

            this._rpc({
                    model: 'hr.employee',
                    method: 'update_work_trip',
                    args: [[self.employee.id],'end',this.$( ".reasons" ).val()]
                })
                .then(function(result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                    }
                });
                location.reload();

        },
    });
    
    core.action_registry.add('hr_attendance_action_work_trips', MyAttendances);
    return MyAttendances;
    
    });
    