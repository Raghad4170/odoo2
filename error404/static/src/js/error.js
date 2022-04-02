odoo.define('error404.error', function (require) {
    "use strict";


    var ajax = require('web.ajax');
    var session = require('web.session');

    // alert(session.user_id)
    $(document).ready(function(){	


          $(document).on("click",'.submit_msg_error' ,function(){
            var status_message = $('#status_message').val();
          
            var node = document.getElementById('status_message')

            
            var textContent = node.textContent


            var status_name = $('#status_name').val();
          
            var name_node = document.getElementById('status_name')

            
            var NodetextContent = name_node.textContent
            // alert(textContent)
            // alert(status_message)

              var dict={}
              dict['status_message']=textContent
              dict['user_id']=session.user_id
              dict['status_name']=status_name
            
              ajax.jsonRpc('/submit_err_msg', 'call',{'kw':dict}).then(function(data) {
                return window.location = '/';
 

            });

 
          });


    });

});
