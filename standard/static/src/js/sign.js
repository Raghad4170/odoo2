odoo.define('standard.sign', function (require) {
    "use strict";
  
    var core = require('web.core');
    var config = require('web.config');
    var utils = require('web.utils');
    var Widget = require('web.Widget');
    var ajax = require('web.ajax');
    var qweb = core.qweb;
    var publicWidget = require('web.public.widget');
    var Dialog = require('web.Dialog');
    var session = require('web.session');
    $(document).ready(function () { 

    $('#button1').on('click', function() {
        $('#openModal').show();
    });
});

})
   
