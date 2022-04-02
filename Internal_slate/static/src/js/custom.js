odoo.define('internal_slate.custom', function (require) {
  'use strict';
  var core = require('web.core');
  var QWeb = core.qweb;
  var ajax = require('web.ajax');
  
  $(document).ready(function () {
    
    var table = $("table tbody");
  
      table.find('tr').each(function (i) {
          var $tds = $(this).find('td'),
              slate_id = $tds.eq(0).text(),
              service_days = $tds.eq(3).text();
              if ($tds.eq(5).text()=='slat_only')
              {
              if ( $.isNumeric(slate_id)){

            if (slate_id)
            {
  
            ajax.jsonRpc('/get_date', 'call',{'slate_id':slate_id}).then(function(data) { 
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
            $tds.eq(3).html("<div style='text-align:justify;display:flex;justify-content:center;margin-top:5px;'>"+
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
              $tds.eq(3).text("سيتم تقديمها في أقرب وقت");
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
  
  
  
  