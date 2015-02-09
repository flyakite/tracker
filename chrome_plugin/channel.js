
var zenblip = (function(zb) {

  var channelToken,
    clientID,
    _renewTimer = 60*60*1000, //renew per hour(google times out per 2 hour)
    _initTimer = 1*1000, //1 second
    timerCount = _initTimer;

  // var xhRequest = function(method, url, callback){
  //   var xhr;
  //   if(window.XMLHttpRequest){
  //     xhr = new XMLHttpRequest();
  //   }else{
  //     //IE5, 6, maybe we don't need to support this
  //     xhr = new ActiveXObject("Microsoft.XMLHTTP");
  //   }
  //   xhr.onreadystatechange = function(){
  //     if(xhr.readyState == xhr.DONE){
  //       if(xhr.status == 200){
  //         callback(xhr.responseText);
  //       }else{
  //         console.log("xhr Error 1");
  //       }
  //     }
  //   };
  //   xhr.open(method, url, true);
  //   xhr.send(null);
  // };

  // get around net::ERR_CONNECTION_RESET problem


  var performing = false;
  zb.createNewChannelToken = function(options, callback){
    if(!performing){
      setTimeout(function(){
        performing = false;
        zb.getOrCreateChannelToken(options, function() {
          options.isCreate = true;
          if(callback && typeof callback == 'function'){
            callback(options);
          }
        });
      }, timerCount);
      console.log('reconnect after ' + timerCount/1000 +' seconds');
      timerCount = Math.pow(timerCount, 2);
      performing = true;
    }
  };

  zb.getOrCreateChannelToken = function(options, callback){
    /* JSON.parse browser support:
     Feature  Chrome  Firefox (Gecko) Internet Explorer   Opera   Safari
     Basic support(Yes)   3.5 (1.9.1)  8.0         10.5  4.0
    * */
    /* 
      options: isCreate, senderEmail
    */
    var path = options.isCreate? "create_token":"get_token";
    console.log('getOrCreateChannelToken ' + path);
    zb.retryConnection.hold('getOrCreateChannelToken', 30*1000, function(){
      zb.getOrCreateChannelToken(options, callback);
    });
    $.post(options.uri+path, {owner:options.senderEmail}, function(jdata){
      console.log('got channel token');
      zb.retryConnection.release('getOrCreateChannelToken');
      console.log(jdata);
      if(jdata.error){
        console.log(jdata.error);
        zb.createNewChannelToken(options, callback);
        if(callback && typeof callback == 'function'){
          callback();
        }
      }else{
        channelToken = jdata.channel_token;
        clientID = jdata.client_id;
        timerCount = 1000;
        if(callback && typeof callback == 'function'){
          callback();
        }
      }
    });
  };
  var onOpened = function() {
    connected = true;
     // sendMessage('opened');
    console.log("channel opened");
    // setTimeout(function(){
    //   getOrCreateChannelToken(openChannel, true);
    // }, _renewTimer);
    timerCount = _initTimer;
  };
  var onMessage = function(jmsg) {
    //TODO: change to use messenger
    console.log('onMessage');
    console.log(jmsg);
    // chrome.runtime.sendMessage({msg:jmsg});
    document.dispatchEvent(new CustomEvent('zbNotificationMessage', {
      detail:{'e':'zbNotificationMessage',
      'jmsg':jmsg}
    }));
    // $(document.body).data('zbMsg', jmsg);
    // $("#messages ul").append($("<li></li>").html(msg.data));

  };
  var onError = function(err, options) {
    console.log("channel Got error");
    console.log(err);
    if(err && (err.code == 401 || err.code == 400)){
      options.isCreate = true;
      zb.getOrCreateChannelToken(options, function() {
        zb.openChannel(options);
      });
    }
  };
  var onClose = function() {
     // alert("close");
   //   connected = false;
    console.log("channel closed");
  };
  // open new session
  zb.openChannel = function(options){
    console.log('openChannel: ' + channelToken);
    var channel = new goog.appengine.Channel(channelToken);
    var socket = channel.open();
    socket.onopen = onOpened;
    socket.onmessage = onMessage;
    socket.onerror = function(err) {
      onError(err, options);
    };
    socket.onclose = onClose;
  };


  // var registerTab = function(){
  //   console.log(chrome);
  //   console.log(chrome.extension);
  //   console.log(chrome.runtime);
  //   chrome.extension.sendMessage({action:'register'}); //chrome.extension undefined
  //   chrome.runtime.sendMessage({action:'register'}); //chrome.runtime undefined
  // }
  return zb;
}(zenblip || {}));