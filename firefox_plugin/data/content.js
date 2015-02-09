function loadContentScripts(resourcePath){

  // var zbBaseURL = 'https://zenblip.appspot.com';
  // var h = document.createElement('script');
  // h.src = zbBaseURL + '/_ah/channel/jsapi';
  // (document.head || document.documentElement).appendChild(h);

  var j = document.createElement('script');
  j.src = resourcePath['jquery-1.10.2.min.js'];
  (document.head || document.documentElement).appendChild(j);

  var g = document.createElement('script');
  g.src = resourcePath['gmail.js'];
  (document.head || document.documentElement).appendChild(g);

  // var s;
  // h.onload = function(){
  //     s = document.createElement('script');
  //     s.src = resourcePath['contentMain.js'];
  //     (document.head || document.documentElement).appendChild(s);
  // };

  var s = document.createElement('script');
  s.src = resourcePath['contentMain.js'];
  (document.head || document.documentElement).appendChild(s);

  var style = document.createElement('style');
  var cssText = " \
  .tracked-send-buton{ \
    background-color: #594 !important; \
    background-image: -webkit-linear-gradient(top,#594,#584) !important; \
    background-image: -moz-linear-gradient(top,#594,#584) !important; \
    border: 1px solid #393 !important; \
  } \
  .tracked-send-buton:hover{ \
    background-color: #5a4 !important; \
    background-image: -webkit-linear-gradient(top,#5a5,#272) !important; \
    background-image: -moz-linear-gradient(top,#5a5,#272) !important; \
    border: 1px solid #181 !important; \
  } \
  ";
  style.type = 'text/css';
  (document.head || document.documentElement).appendChild(style);
  if(style.styleSheet){
    style.styleSheet.cssText = cssText;
  }else{
    style.appendChild(document.createTextNode(cssText));
  }


  document.addEventListener('zbNotificationMessage', function(e){
      console.log('Content script got event!!!!!');
      console.log(e);
      console.log(e.detail);
      chrome.runtime.sendMessage(null, e.detail);
  });
}
