odoo.define('litigation.consulting', function (require) {
  "use strict";

  var ajax = require('web.ajax');

  var rating;
  var consulting_id=$('input[name="consulting_id"]').val()
  // alert(consulting_id)

  if (consulting_id != undefined ||consulting_id != null) {



    ajax.jsonRpc('/consulting_state', 'call',{consulting_id}).then(function(data) {
      // alert(data)
      if (data=='close')
      {

        $('#rate_2').show()
        $('#close_rate_2').hide()
      
      }
      if (data!='close')
      {

        $('#rate_2').hide()
        $('#save_notes_fivestar_li_2').hide()
        $('#close_rate_2').show()

      
      }

    });

    ajax.jsonRpc('/consulting_rating', 'call',{consulting_id}).then(function(data) {



      


              ajax.jsonRpc('/visblity_close_button_consulting', 'call',{consulting_id}).then(function(data) {
                // alert(data)
                if (data==true)
                {
                  // $('#save_notes_fivestar_li_2').show()

                }
              })


              if (data=='1')
              {
                document.getElementById("s1_2").style.color ='#c59b08' 

              }

              if (data=='2')
              {
                document.getElementById("s1_2").style.color ='#c59b08' 
                document.getElementById("s2_2").style.color ='#c59b08' 

              }

              if (data=='3')
              {
                document.getElementById("s1_2").style.color ='#c59b08' 
                document.getElementById("s2_2").style.color ='#c59b08' 
                document.getElementById("s3_2").style.color ='#c59b08' 

              }
              if (data=='4')
              {
                document.getElementById("s1_2").style.color ='#c59b08' 
                document.getElementById("s2_2").style.color ='#c59b08' 
                document.getElementById("s3_2").style.color ='#c59b08' 
                document.getElementById("s4_2").style.color ='#c59b08' 


              }
              if (data=='5')
              {
                document.getElementById("s1_2").style.color ='#c59b08' 
                document.getElementById("s2_2").style.color ='#c59b08' 
                document.getElementById("s3_2").style.color ='#c59b08' 
                document.getElementById("s4_2").style.color ='#c59b08' 
                document.getElementById("s5_2").style.color ='#c59b08' 


              }

                });
              }

// $('#close_notes').click(function(){
//   // // alert('lll')
//     $('#MyForm_2').hide();

// });

$(".input-star-rate_2").on("click", function(){
  var $this = $(this); //  assign $(this) to $this
  var ratingValue = $this.val()
  // alert(ratingValue);
  rating=ratingValue
  if (rating!=5)
{

  $('#MyForm_2').show()
  $('#save_notes_fivestar_li_2').hide()

  // $('#MyForm_2').toggle(500);

}
if (rating == 5)
{
  var consulting_id=$('input[name="consulting_id"]').val()

  $('#MyForm_2').hide()

  ajax.jsonRpc('/visblity_close_button_consulting', 'call',{consulting_id}).then(function(data) {
    // alert(data)
    if (data==true)
    {
      $('#save_notes_fivestar_li_2').show()

    }
  })
    ajax.jsonRpc('/close_consulting_fivestar', 'call',{consulting_id}).then(function(data) { 
return true;
          });
          alert("شكرا لثقتكم بنا، ونسعى لتحسين جودة خدماتنا بتوفيق الله ثم بدعمكم.")
          location.reload(); 

}
});


$('#save_notes_2').click(function(){
  var consulting_id=$('input[name="consulting_id"]').val()
  var response=$('textarea[name="review_2"]').val()
  var close_bool=false
  ajax.jsonRpc('/close_consulting_less_fivestar', 'call',{consulting_id,response,rating,close_bool}).then(function(data) { 
              alert("شكرا لثقتكم بنا، ونسعى لتحسين جودة خدماتنا بتوفيق الله ثم بدعمكم.")
              $('#MyForm_2').hide();
              location.reload(); 	

              });


});		
$('#save_notes_close_2').click(function(){
var consulting_id=$('input[name="consulting_id"]').val()
var response=$('textarea[name="review_2"]').val()
var close_bool=true

ajax.jsonRpc('/close_consulting_less_fivestar', 'call',{consulting_id,response,rating,close_bool}).then(function(data) { 
              alert("شكرا لثقتكم بنا، ونسعى لتحسين جودة خدماتنا بتوفيق الله ثم بدعمكم.")
              $('#MyForm_2').hide();
              location.reload(); 	

              });


});


$('#close_rate_2').click(function(){


  $('#rate_2').show()
  $('#close_rate_2').hide()

  ajax.jsonRpc('/visblity_close_button_consulting', 'call',{consulting_id}).then(function(data) {
    // alert(data)

  })

});


$('#save_notes_fivestar_2').click(function(){
var consulting_id=$('input[name="consulting_id"]').val()
var response=false
var close_bool=true
// var rating='5'
                

// alert(rating)

ajax.jsonRpc('/close_consulting_less_fivestar', 'call',{consulting_id,response,rating,close_bool}).then(function(data) { 
              alert("شكرا لثقتكم بنا، ونسعى لتحسين جودة خدماتنا بتوفيق الله ثم بدعمكم.")
              $('#MyForm_2').hide();
              location.reload(); 	

              });

});	

});


