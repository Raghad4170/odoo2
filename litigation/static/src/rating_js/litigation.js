odoo.define('litigation.litigation', function (require) {
    "use strict";

		var ajax = require('web.ajax');

    var rating;
    var litigation_id=$('input[name="litigation_id"]').val()
    // alert(litigation_id)

    if (litigation_id != undefined ||litigation_id != null) {

      ajax.jsonRpc('/generate_tab_data', 'call',{litigation_id}).then(function(data) {
        // alert(data.length)
        if (data.length)
        {
          var msg_box = $('div[name="tab"]')
          var msg_box_two = $('div[name="subtab"]')

          var html_code='';
          var html_code_two='';




          // for (let i = 0; i < data.length; i++) {
          //   html_code+="<button class='tablinks display_tab' id='display_tab' value="+data[i]['name']+'>'+data[i]['name']+'</button>'
          //   html_code_two+="<div id="+data[i]['name']+" class='tabcontent'>  <h3>Summary</h3> <p>"+data[i]['summary']+"</p></div>" 
          // }
          for (let i = 0; i < data.length; i++) {
            html_code+="<button class='tablinks display_tab' id='display_tab' value="+data[i]['id']+'>'+data[i]['name']+'</button>'


            if( data[i]['court_date']  ){
            var courtdate_row='';

            courtdate_row='<tr><th class="text-left pb-0">تاريخ الجلسة:</th><td class="w-100 pb-0 text-wrap"><span/>' +  data[i]['court_date'] + '</span></td></tr>'
              }

              else
              {
                var courtdate_row='';
              }

              if( data[i]['court_type']  ){
              var court_type='';
  
              court_type='<tr><th class="text-left pb-0">نوع الجلسة:</th><td class="w-100 pb-0 text-wrap"><span/>' + data[i]['court_type'] + '</span></td></tr>'

                }
  
                else
                {
                  var court_type='';
                }
                if( data[i]['present_judges']  ){
                  var present_judge='';
      
                  present_judge='<tr><th class="text-left pb-0">القضاة الحاضرين:</th><td class="w-100 pb-0 text-wrap"><span/>' +  data[i]['present_judges'] + '</span></td></tr>'
    
                    }
      
                    else
                    {
                      var present_judge='';
                    }
                    if( data[i]['writer']  ){
                      var writer='';
          
                      writer='<tr><th class="text-left pb-0">أمين السر / الكاتب:</th><td class="w-100 pb-0 text-wrap"><span/>' +  data[i]['writer'] + '</span></td></tr>'        
                        }
          
                        else
                        {
                          var writer='';
                        }
                      if( data[i]['link']  ){
                        var link='';
            
                        link='<tr><th class="text-left pb-0">للاطلاع على المستندات:</th><td class="w-100 pb-0 text-wrap"><span/>' +  data[i]['link'] + '</span></td></tr>'        
                          }
            
                          else
                          {
                            var link='';
                          }   
                      if( data[i]['summary']  ){
                        var summary='';
            
                        summary='<div><h4 class="mb-1">ملخص الجلسة</h4><hr class="my-0"/><div/><div style="text-align: justify;text-justify: inter-word;"/>' +  data[i]['summary'] + '</div>'        
                          }
            
                          else
                          {
                            var summary='';
                          }
            html_code_two+=("<div id=" + data[i]['id'] + " class='tabcontent'>" + '<div><h4 class="mb-1">معلومات الجلسة</h4><hr class="my-0"/><div class="row"><span class="col-12 col-lg-5  mb-3 mb-lg-0"><table class="table table-borderless table-sm"><tbody style="white-space:nowrap">'+courtdate_row+court_type+'</tbody></table></span><span class="col-12 col-lg-5  mb-3 mb-lg-0"><table class="table table-borderless table-sm"><tbody style="white-space:nowrap">'+present_judge+writer+link+'</tbody></table></span></div></div>'+summary+'</div>')
          }
 

          msg_box.append(html_code)
          msg_box_two.append(html_code_two)
          // // alert(msg_box)


       

        }

      });


      ajax.jsonRpc('/litigation_rating', 'call',{litigation_id}).then(function(data) {
                // alert(data)

                if (data=='1')
                {
                  document.getElementById("s1").style.color ='#c59b08' 

                }

                if (data=='2')
                {
                  document.getElementById("s1").style.color ='#c59b08' 
                  document.getElementById("s2").style.color ='#c59b08' 

                }

                if (data=='3')
                {
                  document.getElementById("s1").style.color ='#c59b08' 
                  document.getElementById("s2").style.color ='#c59b08' 
                  document.getElementById("s3").style.color ='#c59b08' 

                }
                if (data=='4')
                {
                  document.getElementById("s1").style.color ='#c59b08' 
                  document.getElementById("s2").style.color ='#c59b08' 
                  document.getElementById("s3").style.color ='#c59b08' 
                  document.getElementById("s4").style.color ='#c59b08' 


                }
                if (data=='5')
                {
                  document.getElementById("s1").style.color ='#c59b08' 
                  document.getElementById("s2").style.color ='#c59b08' 
                  document.getElementById("s3").style.color ='#c59b08' 
                  document.getElementById("s4").style.color ='#c59b08' 
                  document.getElementById("s5").style.color ='#c59b08' 



                }

                  });
                }

  $(".input-star-rate").on("click", function(){
    var $this = $(this); //  assign $(this) to $this
    var ratingValue = $this.val()
    // alert(ratingValue);
    rating=ratingValue
    if (rating!=5)
  {

    $('#MyForm').show()
    $('#save_notes_fivestar_li').hide()

    // $('#MyForm').toggle(500);

  }
  if (rating == 5)
  {

    $('#MyForm').hide()
    var litigation_id=$('input[name="litigation_id"]').val()



    var litigation_id=$('input[name="litigation_id"]').val()
        ajax.jsonRpc('/close_litigation_fivestar', 'call',{litigation_id}).then(function(data) { 
  return true;
            });
            alert("شكرا لثقتكم بنا، ونسعى لتحسين جودة خدماتنا بتوفيق الله ثم بدعمكم.")
            location.reload();
  }
});


  $('#save_notes').click(function(){
    var litigation_id=$('input[name="litigation_id"]').val()
    var response=$('textarea[name="review"]').val()
    ajax.jsonRpc('/close_litigation_less_fivestar', 'call',{litigation_id,response,rating}).then(function(data) { 
                alert("شكرا لثقتكم بنا، ونسعى لتحسين جودة خدماتنا بتوفيق الله ثم بدعمكم.")
                $('#MyForm').hide();
                location.reload(); 	

                });

});		

$('#save_notes_fivestar').click(function(){
  var litigation_id=$('input[name="litigation_id"]').val()
  var response=false
  ajax.jsonRpc('/close_litigation_less_fivestar', 'call',{litigation_id,response,rating}).then(function(data) { 
                alert("شكرا لثقتكم بنا، ونسعى لتحسين جودة خدماتنا بتوفيق الله ثم بدعمكم.")
                $('#MyForm').hide();
                location.reload(); 	

                });

});
$(document).on("click",'.display_tab' ,function(){
    var $this = $(this); //  assign $(this) to $this

  // alert( $this.val())
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById( $this.val()).style.display = "block";
  // evt.currentTarget.className += " active";
});		

});

