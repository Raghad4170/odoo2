odoo.define('litigation.url_replacement', function (require) {
    "use strict";


    function urlify(text) {
      var urlRegex = /(https?:\/\/[^\s]+)/g;
      return text.replace(urlRegex, function(url) {
        return '<a href="' + url + '"  target="_blank">' + url + '</a>';
      })
    
    }
    // alert(document.getElementById('content'))
    var node = document.getElementById('content')
    if (node != null)
    {
    var htmlContent = node.innerHTML
    
    var textContent = node.textContent
    // alert(textContent)
    document.getElementById('content').innerHTML=urlify(textContent)
    }

});

