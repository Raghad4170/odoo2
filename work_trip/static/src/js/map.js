odoo.define('work_trip.map', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var core = require('web.core');

    var qweb = core.qweb;
    var time = require('web.time');

    var AbstractAction = require('web.AbstractAction');
    var field_utils = require('web.field_utils');
    
    ajax.loadXML('/work_trip/static/src/map.xml', qweb);
    
    // alert("lllllllllllll")

    
   var map = AbstractAction.extend({
    contentTemplate: 'OdooMap',
    events: {
        "click .submit": _.debounce(function() {
            this.submit_coordinates();
        }, 200, true),
        
       
    },
    submit_coordinates: function () {
        var self = this;
     
        self._rpc({
                model: 'res.users',
                method: 'submit_coordinates',
                args: [self.user_id,self.user_id,self.$( ".lat" ).val(),self.$( ".long" ).val(),self.$( ".meter" ).val()]
            })
            .then(function(result) {
                       alert("تم إعتماد الإحداثيات")

            });

    },

    init: function (parent, action) {
        this._super.apply(this, arguments);
        var context = action.context;
        this.user_id = context.user_id;
    },


});


      
      core.action_registry.add('hr_attendance_action_map', map);
      return map;
  
});
