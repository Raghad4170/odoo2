odoo.define('avatar.leave', function(require) {
    'use strict';
    // alert('I am In')
    var ajax = require('web.ajax');
    $(document).ready(function(){	




            var selected = $('select[name="timeoff_type"]')
            // alert(selected)
            if(selected) {
                selected.change(function(){

                    ajax.jsonRpc('/get/time_type', 'call', {'timeoff_id':$(this).val()}).then(function(data) { 
					
						if(data) {
							
                            $('.check_hours').show()

						}
	                });
                    // check_hours_days

                })
            }


            var from_days = $('select[name="day_type"]')
            // alert($(this).val())
            if(from_days) {
                from_days.change(function(){
                    $('.date_to').hide()

                    if ($(this).val()=='custom_hours')
                    {

                    $('.check_hours_days').show()
                    $('.request_date_from_period').hide()


                    // check_hours_days
                    }
                    else
                    {
                        $('.request_date_from_period').show()
                        $('.check_hours_days').hide()


                    }

                })
            }
    });
});

