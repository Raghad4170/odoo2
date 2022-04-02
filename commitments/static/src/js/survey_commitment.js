odoo.define('commitments.survey_commitments', function (require) {
    "use strict";

		var ajax = require('web.ajax');
    window.history.forward();
    function noBack() {
        window.history.forward();
    }    $('#container_1').on('click', 'input[type="radio"]', function() {
      this.name = this.className;
      var radio_value=$(this).val()
      if (radio_value=="اخرى")
      {
        $('.'+this.name+'_text').show()
        $('.'+this.name+'_text').required = true;    
      }
      else
      {
        $('.'+this.name+'_text').hide()
      }
      if (radio_value == 'غير ملتزم')
      {
        $('.'+this.name+'_container_ot').show()       
      }
      else
      {
        $('.'+this.name+'_container_ot').hide()
      }
      if (radio_value =='ملتزم')
      {
        $('.'+this.name+'_container_ot_text').prop('required',false);
        $('.'+this.name+'_container_ot_text').hide()
      }
  });
    
$('#containers_1').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
  if (radio_value=="اخرى")
  {
    $('.'+this.name+'_text').show()
    $('.'+this.name+'_text').prop('required',true);
  }
  else
  {
    $('.'+this.name+'_text').hide()
  }
  if (radio_value == 'غير ملتزم')
  {
    $('.'+this.name+'_container_ot').show() 
    $('.'+this.name+'_container_ot').required = true;    
  }
  else
  {
    $('.'+this.name+'_container_ot').hide()
  }
});

$('#container_2').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_2').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_3').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_3').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});

$('#container_4').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_4').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_5').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_5').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_6').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_6').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_7').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_7').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_8').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_8').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_9').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_9').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_10').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_10').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_11').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_11').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_12').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_12').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_13').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_13').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_14').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_14').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_15').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_15').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_16').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_16').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_17').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_17').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_18').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_18').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_19').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_19').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_20').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_20').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_21').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_21').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_22').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_22').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_23').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_23').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_24').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_24').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_25').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_25').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_26').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_26').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_27').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_27').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_28').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_28').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_29').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_29').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_30').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_30').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_31').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_31').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_32').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_32').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_33').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_33').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_34').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_34').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_35').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_35').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_36').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_36').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_37').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_37').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_38').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_38').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_39').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_39').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_40').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_40').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_41').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_41').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_42').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_42').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_43').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_43').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_44').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_44').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_45').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_45').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_46').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_46').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_47').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_47').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_48').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_48').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_49').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_49').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_50').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_50').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_51').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_51').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_52').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_52').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_53').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_53').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_54').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_54').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_54').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_55').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_56').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_56').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_57').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_57').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_58').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_58').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_59').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_59').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_60').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_60').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_61').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_61').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_62').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_62').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_63').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_63').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_64').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_64').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_65').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_65').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_66').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_66').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_67').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_67').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_68').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_68').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_69').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_69').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_70').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_70').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_71').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_71').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_72').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_72').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_73').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_73').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_74').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_74').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_75').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_75').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_76').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_76').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_77').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_77').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_78').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_78').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_79').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_79').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_80').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_80').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_81').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_81').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_82').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_82').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_83').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_83').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_84').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_84').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_85').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_85').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_86').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_86').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_87').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_87').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_88').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_88').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_89').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_89').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_90').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_90').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_91').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_91').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_92').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_92').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_93').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_93').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_94').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_94').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_95').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_95').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_96').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_96').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_97').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_97').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_98').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_98').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_99').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_99').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});
$('#container_100').on('click', 'input[type="radio"]', function() {
  this.name = this.className;
  var radio_value=$(this).val()
    if (radio_value=="اخرى")
    {
      $('.'+this.name+'_text').show()
    }
    else
    {
      $('.'+this.name+'_text').hide()
    }
  if (radio_value == 'غير ملتزم')
  {
         $('.'+this.name+'_container_ot').show()     
  }
  else
  {
      $('.'+this.name+'_container_ot').hide()
  }
  if (radio_value =='ملتزم')
  {
    $('.'+this.name+'_container_ot_text').prop('required',false);

    $('.'+this.name+'_container_ot_text').hide()
  }
});
  
$('#containers_100').on('click', 'input[type="radio"]', function() {
this.name = this.className;
var radio_value=$(this).val()
if (radio_value=="اخرى")
{
  $('.'+this.name+'_text').show()
  $('.'+this.name+'_text').prop('required',true);
}
else
{
  $('.'+this.name+'_text').hide()
}
if (radio_value == 'غير ملتزم')
{
     $('.'+this.name+'_container_ot').show()     
}
else
{
  $('.'+this.name+'_container_ot').hide()
}
});

});