odoo.define('work_trip.trip_geo', function (require) {
    "use strict";

    const trip = require('work_trip.work_trip');
    

    trip.include({
        start_work_trip(){
            var self = this;
            var options = {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            };
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(self.update_work_trip.bind(self), self._getPositionError, options);
            }
        },
        update_work_trip(position){
            var self = this;
            this._rpc({
                model: 'hr.employee',
                method: 'update_work_trip',
                args: [[self.employee.id],'start',this.$( ".reasons" ).val(), [position.coords.latitude, position.coords.longitude]],
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
// end
        end_work_trip(){
            var self = this;
            var options = {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            };
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(self.update_end_work_trip.bind(self), self._getPositionError, options);
            }
        },
        update_end_work_trip(position){
            var self = this;
            this._rpc({
                model: 'hr.employee',
                method: 'update_work_trip',
                args: [[self.employee.id],'end',this.$( ".reasons" ).val(), [position.coords.latitude, position.coords.longitude]],
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
        
        _getPositionError(err) {
            alert("يجب أن تسمح بالوصول إلى موقعك")
        },
    });

});
