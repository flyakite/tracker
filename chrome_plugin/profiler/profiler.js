$(document).ready(function() {
  var r = document.getElementById('relationship')
  if(r && r.innerHTML){
    $.post('https://www.zenblip.com/profiler/spr', {
        url:document.location.href, 
        content:document.getElementsByTagName('html')[0].innerHTML},
        function() {
          
        });
  }
})