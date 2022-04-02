odoo.define('litigation.contraconsulting', function (require) {
    "use strict";

		var ajax = require('web.ajax');

    var rating;
    var contractconsulting_id=$('input[name="contractconsulting_id"]').val()
    // alert(contractconsulting_id)

    if (contractconsulting_id != undefined ||contractconsulting_id != null) {

      ajax.jsonRpc('/contra_consulting_state', 'call',{contractconsulting_id}).then(function(data) {
        // alert(data)
        if (data=='close')
        {
  
          $('#rate_3').show()
          $('#close_rate_3').hide()
        
        }
        if (data!='close')
        {
  
          $('#rate_3').hide()
          $('#close_rate_3').show()
  
        
        }
  
      });

      ajax.jsonRpc('/contractconsulting_rating', 'call',{contractconsulting_id}).then(function(data) {



        ajax.jsonRpc('/visblity_close_button_contractconsulting', 'call',{contractconsulting_id}).then(function(data) {
          // alert(data)
          if (data==true)
          {
            $('#save_notes_fivestar_li_3').show()

          }
        })
        
                if (data=='1')
                {
                  document.getElementById("s1_3").style.color ='#c59b08' 

                }

                if (data=='2')
                {
                  document.getElementById("s1_3").style.color ='#c59b08' 
                  document.getElementById("s2_3").style.color ='#c59b08' 

                }

                if (data=='3')
                {
                  document.getElementById("s1_3").style.color ='#c59b08' 
                  document.getElementById("s2_3").style.color ='#c59b08' 
                  document.getElementById("s3_3").style.color ='#c59b08' 

                }
                if (data=='4')
                {
                  document.getElementById("s1_3").style.color ='#c59b08' 
                  document.getElementById("s2_3").style.color ='#c59b08' 
                  document.getElementById("s3_3").style.color ='#c59b08' 
                  document.getElementById("s4_3").style.color ='#c59b08' 


                }
                if (data=='5')
                {
                  document.getElementById("s1_3").style.color ='#c59b08' 
                  document.getElementById("s2_3").style.color ='#c59b08' 
                  document.getElementById("s3_3").style.color ='#c59b08' 
                  document.getElementById("s4_3").style.color ='#c59b08' 
                  document.getElementById("s5_3").style.color ='#c59b08' 


                }

                  });
                }

  // $('#close_notes').click(function(){
  //   // // alert('lll')
  //     $('#MyForm_3').hide();

  // });
  $('#close_rate_3').click(function(){

    $('#rate_3').show()
    $('#close_rate_3').hide()
  
    ajax.jsonRpc('/visblity_close_button_contra_consulting', 'call',{contractconsulting_id}).then(function(data) {
      // alert(data)
  
    })
  
  });

  $(".input-star-rate_3").on("click", function(){
    var $this = $(this); //  assign $(this) to $this
    var ratingValue = $this.val()
    // alert(ratingValue);
    rating=ratingValue
    if (rating!=5)
  {

    $('#MyForm_3').show()
    $('#save_notes_fivestar_li_3').hide()

    // $('#MyForm_3').toggle(500);

  }
  
  if (rating == 5)
  {
    var contractconsulting_id=$('input[name="contractconsulting_id"]').val()

    $('#MyForm_3').hide()
    ajax.jsonRpc('/visblity_close_button_contractconsulting', 'call',{contractconsulting_id}).then(function(data) {
      // alert(data)
      if (data==true)
      {
        $('#save_notes_fivestar_li_3').show()

      }
    })
      ajax.jsonRpc('/close_contractconsulting_fivestar', 'call',{contractconsulting_id}).then(function(data) { 
  return true;
            });
            alert("شكرا لثقتكم بنا، ونسعى لتحسين جودة خدماتنا بتوفيق الله ثم بدعمكم.")
            location.reload(); 

  }
});


  $('#save_notes_3').click(function(){
    var contractconsulting_id=$('input[name="contractconsulting_id"]').val()
    var response=$('textarea[name="review_3"]').val()
    var close_bool=false
    ajax.jsonRpc('/close_contractconsulting_less_fivestar', 'call',{contractconsulting_id,response,rating,close_bool}).then(function(data) { 
                alert("شكرا لثقتكم بنا، ونسعى لتحسين جودة خدماتنا بتوفيق الله ثم بدعمكم.")
                $('#MyForm_3').hide();
                location.reload(); 	

                });

});		
$('#save_notes_close_3').click(function(){
  var contractconsulting_id=$('input[name="contractconsulting_id"]').val()
  var response=$('textarea[name="review_3"]').val()
  var close_bool=true

  ajax.jsonRpc('/close_contractconsulting_less_fivestar', 'call',{contractconsulting_id,response,rating,close_bool}).then(function(data) { 
                alert("شكرا لثقتكم بنا، ونسعى لتحسين جودة خدماتنا بتوفيق الله ثم بدعمكم.")
                $('#MyForm_3').hide();
                location.reload(); 	

                });

});		


$('#save_notes_fivestar_3').click(function(){
  var consulting_id=$('input[name="contractconsulting_id"]').val()
  var response=false
  var close_bool=true
  // var rating='5'
                  

  // alert(rating)

  ajax.jsonRpc('/close_contractconsulting_less_fivestar', 'call',{contractconsulting_id,response,rating,close_bool}).then(function(data) { 
                alert("شكرا لثقتكم بنا، ونسعى لتحسين جودة خدماتنا بتوفيق الله ثم بدعمكم.")
                $('#MyForm_3').hide();
                location.reload(); 	

                });

});	

});