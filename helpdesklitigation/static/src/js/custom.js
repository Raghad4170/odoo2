odoo.define('helpdesklitigation.custom', function (require) {
  'use strict';
  var core = require('web.core');
  var QWeb = core.qweb;
  
  var ajax = require('web.ajax');
    
    
  //alert("hello")
  $(document).ready(function () {
    
    $(".service_standard").on("click", function(){
      var $this = $(this); //  assign $(this) to $this
      var service_standard = $this.val()
      // alert(service_standard);
      var ticket_type_id=$('input[name="ticket_type_id"]:checked').val()
      // alert(ticket_type_id)
      if (ticket_type_id)
      {
      ajax.jsonRpc('/get_service_cost', 'call',{ticket_type_id,service_standard}).then(function(data) { 
  
        // $('input[name="service_rate"]').val()=data
        if (service_standard == 'عادي')
        {
        document.getElementById('normal_service_rate').textContent=data
        document.getElementById('urgent_service_rate').textContent=''
        document.getElementById('very_urgent_service_rate').textContent=''
        }
  
        if (service_standard == 'مستعجل')
        {
        document.getElementById('urgent_service_rate').textContent=data
        document.getElementById('very_urgent_service_rate').textContent=''
        document.getElementById('normal_service_rate').textContent=''
        }
  
        if (service_standard == 'طارئ')
        {
        document.getElementById('very_urgent_service_rate').textContent=data
        document.getElementById('urgent_service_rate').textContent=''
        document.getElementById('normal_service_rate').textContent=''
        }
  
                  });
        }
  
    
    });
  
    $(".ticket_types").on("click", function(){
      var $this = $(this); //  assign $(this) to $this
      var ticket_type_id = $this.val()
      var service_standard=$('input[name="service_standard"]:checked').val()
   
  
      var text=' <div class="form-group col-12 s_website_form_field s_website_form_model_required" data-type="int" data-name="Field"><div class="row s_col_no_resize s_col_no_bgcolor"><label class="col-form-label col-auto s_website_form_label" style="width: 200px" for="types_ids"><span class="s_website_form_label_content">نوعها</span><span class="s_website_form_mark"> *</span></label><div class="row col-sm col-xs-12">';
      var i=0;
        ajax.jsonRpc('/get_ticket_types_ids', 'call',{ticket_type_id}).then(function(data) { 
          if (data.length)
          {
            var len;
            len=data.length
            for (; i < len; i++) {
              text += "<div class='col-auto'> <input  type='radio' id='types_ids' name='types_ids' class='types_ids' value='"+data[i]['id']+"'/> <label for='types_ids'>"+data[i]['name']+"</label> </div>";
            }
            document.getElementById("ticket_type_data").innerHTML = text+'</div></div>'

          }
          else
          {
            document.getElementById("ticket_type_data").innerHTML =''
          }
      

                    });
      // alert(service_standard)                                                                          
      if (service_standard)
      {
      ajax.jsonRpc('/get_service_cost', 'call',{ticket_type_id,service_standard}).then(function(data) { 
  
        // $('input[name="service_rate"]').val()=data
  
        if (service_standard == 'عادي')
        {
        document.getElementById('normal_service_rate').textContent=data
        document.getElementById('urgent_service_rate').textContent=''
        document.getElementById('very_urgent_service_rate').textContent=''
        }
  
        if (service_standard == 'مستعجل')
        {
        document.getElementById('urgent_service_rate').textContent=data
        document.getElementById('very_urgent_service_rate').textContent=''
        document.getElementById('normal_service_rate').textContent=''
        }
  
        if (service_standard == 'طارئ')
        {
        document.getElementById('very_urgent_service_rate').textContent=data
        document.getElementById('urgent_service_rate').textContent=''
        document.getElementById('normal_service_rate').textContent=''
        }                });
  
  
                }
  
                  if (!service_standard)
      {
      var service_standard='عادي'
      ajax.jsonRpc('/get_service_cost', 'call',{ticket_type_id,service_standard}).then(function(data) { 
        document.getElementById('normal_service_rate').textContent=data

        // alert(data)
      });
      service_standard='مستعجل'
      ajax.jsonRpc('/get_service_cost', 'call',{ticket_type_id,service_standard}).then(function(datam) { 
  
        // alert(datam)
        document.getElementById('urgent_service_rate').textContent=datam

   
        });
        service_standard='طارئ'
        ajax.jsonRpc('/get_service_cost', 'call',{ticket_type_id,service_standard}).then(function(datan) { 
        // alert(datan)
        document.getElementById('very_urgent_service_rate').textContent=datan

                    });
  
  
  
                }
    
  
    
    });
  
  
    var table = $("table tbody");
  
      table.find('tr').each(function (i) {
          var $tds = $(this).find('td'),
              ticket_id = $tds.eq(0).text(),
              service_days = $tds.eq(2).text();
              var helpdesk_litigation = $tds.eq(3).text();

              // alert(helpdesk_litigation)

          if (helpdesk_litigation=='helpdesk_litigation')
          {
  
          if ( $.isNumeric(service_days)){
            if (ticket_id)
            {
  
            ajax.jsonRpc('/get_service_date', 'call',{'ticket_id':ticket_id}).then(function(data) { 
              // alert(data)
              if(data!=false) {
          // Set the date we're counting down to
          
          var countDownDate = new Date(data).getTime();
          
          // Update the count down every 1 second
          var x = setInterval(function() {
          
            // Get today's date and time
            var now = new Date().getTime();
          
            // Find the distance between now and the count down date
            var distance = countDownDate - now;
          
            // Time calculations for days, hours, minutes and seconds
            var days = Math.floor(distance / (1000 * 60 * 60 * 24));
            var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);
            var outputDays =  (days < 10 ? '0' + days : days);
            var outputHours =  (hours < 10 ? '0' + hours : hours);
            var outputMinutes = (minutes < 10 ? '0' + minutes : minutes);
            var outputSeconds = (seconds < 10 ? '0' + seconds : seconds);
            $tds.eq(2).html("<div style='text-align:justify;display:flex;justify-content:center;margin-top:5px;'>"+
                            "<div><h6>"
                            +outputDays+"</h6></div><sup style='margin-top:10px;font-size:11px;margin-left:5px;'>يوم</sup>"+
                            "<div><h6>"
                            +outputHours+"</h6></div><sup style='margin-top:10px;font-size:11px;margin-left:5px;'>ساعة</sup>"+
                            "<div><h6>"
                            +outputMinutes+"</h6></div><sup style='margin-top:10px;font-size:11px;margin-left:5px;'>دقيقة</sup>"+
                            "<div style='margin-left:3px;width:25px;'><h6>"
                            +outputSeconds+"</h6></div><sup style='margin-top:10px;font-size:11px;'>ثانية</sup>"
                            +"</div>")
            // If the count down is finished, write some text
            if (distance < 0) {
              clearInterval(x);
              $tds.eq(2).text("سيتم تقديمها في أقرب وقت");
            }
          }, 1000);
        }
          
        });
          } 
          }
        }
  
          
      });
  
  
  });
  
  
  });
  
  
  
  