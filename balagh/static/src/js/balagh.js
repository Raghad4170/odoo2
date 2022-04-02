odoo.define('balagh.balagh', function(require) {
    'use strict';
    // alert('I am In')
    var ajax = require('web.ajax');
    $(document).ready(function(){	


          $(document).on("click",'.submit_msg' ,function(){
            var fieldValue = $('#recever_id').val();
            var email = $('#email').val();
            var count = fieldValue.length;
         
            if (count <10)
            {
                alert("تأكد من صحة رقم الهوية")
                return false
            }

            if($('#recever_name').val().split(' ').length < 2)

            {
                alert("اسم المستقبل يجب أن يتكون من اسمين على الأقل")
                return false

            }

            if($('#sender_name').val().split(' ').length < 2)

            {
                alert("اسم المرسل يجب أن يتكون من اسمين على الأقل")
                return false
            }           


              var dict={}
              dict['recever_id']=$('#recever_id').val()
              dict['recever_name']= $('#recever_name').val()
              dict['sender_name']=$('#sender_name').val(),
              dict['msg_id']=$('#msg_id').val()
              dict['m1']=$('#m1').val()
              dict['m2']=$('#m2').val()
              dict['m3']=$('#m3').val()
              dict['m4']=$('#m4').val()
              dict['m5']=$('#m5').val()
              dict['m6']=$('#m6').val()
              dict['m7']=$('#m7').val()
              dict['m8']=$('#m8').val()
              dict['email']=$('#email').val()
              dict['phone']=$('#phone').val()


              ajax.jsonRpc('/submit_balag_msg', 'call',{'kw':dict}).then(function(data) {
                return window.location = '/balagh_sucsess';
 

            });

 
          });


            var selected = $('input[name="message_data"]').val();
            var msg_box = $('div[name="msg_box"]')
            if (selected!== null  &&  selected !== undefined)
            {
            var selected_one=selected.replace("#8", "<input type='text' id='m8' name='m8' size='10' required='True'/>")
            var selected_two=selected_one.replace("#7","<input type='text' id='m7' name='m7'  size='10' required='True'/>")
            var selected_three=selected_two.replace("#6","<input type='text' id='m6' name='m6' size='10'  required='True'/>")
            var selected_four=selected_three.replace("#5", "<input type='text' id='m5' name='m5' size='10' required='True'/>")
            var selected_five=selected_four.replace("#4","<input type='text' id='m4' name='m4'  size='10' required='True'/>")
            var selected_six=selected_five.replace("#3", "<input type='text' id='m3' name='m3' size='10' required='True'/>")
            var selected_seven=selected_six.replace("#2","<input type='text' id='m2' name='m2'  size='10' required='True'/>")
            var selected_eight=selected_seven.replace("#1","<input type='text' id='m1' name='m1' size='10'  required='True'/>")

            msg_box.append(selected_eight)
            }
    });
});

