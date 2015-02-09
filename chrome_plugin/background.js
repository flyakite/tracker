// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

/*
  Displays a notification with the current time. Requires "notifications"
  permission in the manifest file (or calling
  "Notification.requestPermission" beforehand).
*/
var zbBaseURL = 'https://zenblip.appspot.com';

var j = document.createElement('script');
j.src = chrome.extension.getURL('jquery-1.10.2.min.js');
(document.head || document.documentElement).appendChild(j);

// var h = document.createElement('script');
// h.src = zbBaseURL + '/_ah/channel/jsapi';
// (document.head || document.documentElement).appendChild(h);

// var m = document.createElement('script');
// m.src = chrome.extension.getURL('backgroundMain.js');
// (document.head || document.documentElement).appendChild(m);

//load google api after backgroundMain.js
//var n = document.createElement('script');
//n.src = 'https://apis.google.com/js/client.js?onload=gapiInit';
//(document.head || document.documentElement).appendChild(n);


// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

/*
  Displays a notification with the current time. Requires "notifications"
  permission in the manifest file (or calling
  "Notification.requestPermission" beforehand).
*/

/*
{"installed":{"auth_uri":"https://accounts.google.com/o/oauth2/auth",
"token_uri":"https://accounts.google.com/o/oauth2/token",
"client_email":"",
"redirect_uris":["urn:ietf:wg:oauth:2.0:oob","oob"],
"client_x509_cert_url":"",
"client_id":"709499323932-fiasgo5aeh369gko480h7s17v63glgok.apps.googleusercontent.com",
"auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs"}}
*/

//oauth scope
//https://developers.google.com/accounts/docs/OAuth2Login#scope-param

// var zbBaseURL = 'http://127.0.0.1:8888';
var zbBaseURL = 'https://zenblip.appspot.com'; //deprecate appspot.com because of session
var zbAuthPath = '/auth/google';
var channelToken,
    _renewTimer = 60*60*1000, //renew per hour(google times out per 2 hour)
    _initTimer = 1*1000, //1 second
    timerCount = _initTimer,
    userInfo = null,
    UKeys = [];

// get around net::ERR_CONNECTION_RESET problem
var retryConnectionRegistry = {};
var retryConnection = {
    hold: function(registerID, timeout, callback) {
        console.log('hold' + registerID + ' ' + timeout);
        var control = setTimeout(function() {
            retryConnectionRegistry[registerID] = {};
            callback();
        }, timeout);
        retryConnectionRegistry[registerID] = { 'timeout': timeout,
                                                'control': control};
    },
    release: function(registerID) {
        console.log('release ' + registerID);
        if (retryConnectionRegistry[registerID]){
            // console.log('release control');
            //console.log(retryConnectionRegistry[registerID]);
            clearTimeout(retryConnectionRegistry[registerID].control);
        }
        retryConnectionRegistry[registerID] = {};  
    },

}

// var xhRequest = function(method, url, callback){
//     var xhr;
//     if(window.XMLHttpRequest){
//         xhr = new XMLHttpRequest();
//     }else{
//         //IE5, 6, maybe we don't need to support this
//         xhr = new ActiveXObject("Microsoft.XMLHTTP");
//     }
//     xhr.onreadystatechange = function(){
//         if(xhr.readyState == xhr.DONE){
//             if(xhr.status == 200){
//                 callback(xhr.responseText);
//             }else{
//                 console.log("xhr Error 1");
//             }
//         }
//     };
//     xhr.open(method, url, true);
//     xhr.send(null);
// };
// var getChannelToken = function(callback, isCreate){
//     /* JSON.parse support
//      Feature    Chrome  Firefox (Gecko) Internet Explorer   Opera   Safari
//      Basic support(Yes)   3.5 (1.9.1)    8.0                 10.5    4.0
//      * */
//     var path = isCreate? "create_token":"get_token";
//     xhRequest("GET", zbBaseURL + "/channels/"+path, function(data){
//         console.log('got token');
//         var jdata = JSON.parse(data);
//         if(jdata.error){
//             console.log(jdata.error);
//         }else{
//             channelToken = jdata.token;
//             callback();
//         }
//     });
// };
// var onOpened = function() {
//     connected = true;
//    // sendMessage('opened');
//     console.log("opened");
//     setTimeout(function(){
//         getChannelToken(openChannel, true);
//     }, _renewTimer);
//     timerCount = _initTimer;
// };
// var onMessage = function(msg) {
//     console.log('onMessage');
//     console.log(msg);
//     // $("#messages ul").append($("<li></li>").html(msg.data));

// };
// var onError = function(err) {
//     console.log("Got error");
//     console.log(err);
//     if(err && err.code == 401){
//         setTimeout(function(){
//             getChannelToken(openChannel, true);
//         }, timerCount);
//         console.log('reconnect after ' + timerCount/1000 +' seconds');
//         timerCount = Math.pow(timerCount, 2);
//     }
// };
// var onClose = function() {
//    // alert("close");
//  //   connected = false;
//     console.log("close");
// };
// // open new session
// var openChannel = function(){
//     var channel = new goog.appengine.Channel(channelToken);
//     var socket = channel.open();
//     socket.onopen = onOpened;
//     socket.onmessage = onMessage;
//     socket.onerror = onError;
//     socket.onclose = onClose;
// };

chrome.runtime.onMessage.addListener(function(msg, msgSender, sendResponse){
  console.log(msg);

  switch(msg.e){
    case 'zbNotificationMessage':
      console.log('zbNotificationMessage');
      console.log(msg.jmsg);
      var jmsg = JSON.parse(msg.jmsg.data);
      var title, body;
        if(jmsg.access.accessor_name){
            accessor = jmsg.access.accessor_name;
        }else if(jmsg.access.accessor){
            accessor = jmsg.access.accessor;
        }else{
            accessor = null;
        }
        switch(jmsg.access.kind){
            case 'open':
              title = jmsg.signal.subject;
              if(accessor){
                body = accessor + ' opened the email';
              }else{
                body = 'This email was opened.';
              }
              break;
            case 'link':
              title = jmsg.signal.subject;
              if(accessor){
                body = accessor + ' clicked the link ' + jmsg.access.url;
              }else{
                body = 'Link clicked: ' + jmsg.access.url;
              }
              break;
            default:
              title = jmsg.signal.subject;
              if(accessor){
                body = accessor +' accessed.';
              }else{
                body = 'Email accessed';
              }
        }

        chrome.notifications.create('', {
          type: "basic",
          title: title,
          message: body,
          eventTime: Date.now() + 10*1000, //10 seconds
          iconUrl: "128.png"
        },function(id){
          if(chrome.runtime.lastError){
            console.error(chrome.runtime.lastError);
          }
        });
      break;
    // case 'zbSenderInit':
    //   console.log('zbSelfOpenEmail');
    //   console.log(msg);

    //   //TODO: could be more accruate to match the tab id
    //   if(UKeys.indexOf(msg.ukey) == -1){
    //     UKeys.push(msg.ukey);
    //   }
    //   console.log(UKeys);
    //   break;
    case 'zbGetExtDetails':
      console.log('zbGetExtDetails');
      var zbDetails = chrome.app.getDetails();
      if(sendResponse != 'undefined'){
        sendResponse(zbDetails);
      }
      break;
    default:
      console.log('Message Error!!' + msg.e);
      break;
  }
  
});


chrome.webRequest.onBeforeRequest.addListener(function(details) {
  console.log('onBeforeRequest');
  console.log(details.url);

  var isBlocking = false;
  for(var i in UKeys){
    if(details.url.indexOf('u='+UKeys[i]) != -1){
      isBlocking = true;
    }
  }
  console.log('isBlocking: ' + isBlocking);
  return {'cancel':isBlocking};
  },
  {urls:["*://*.googleusercontent.com/proxy/*"]}, //stop google from knowing, 
  ["blocking"]
);

function getAndUpdateUserInfo (options, callback) {
  console.log('getAndUpdateUserInfo');
  getGoogleAuthToken(options, function(result){
    if(!result.error){
      retryConnection.hold('onGotAuthTokenSendToServer' + result.access_token, 5*1000, function(){
        onGotAuthTokenSendToServer(result.access_token, callback);  
      });
    }else{
      console.log('getGoogleAuthToken Error');
      callback({error:true})
    }
  });
}
/** independent get google auth token function **/
function getGoogleAuthToken(options, callback) {
  console.log('getGoogleAuthToken');
  console.log(options);
  chrome.identity.getAuthToken({ interactive: options.interactive }, function(access_token) {
    if (chrome.runtime.lastError) {
      console.log(chrome.runtime.lastError);
      onGoogleAuthUnauthorized(callback);
      return;
    }
    console.log('Got Google Auth Token');
    // chrome.identity.removeCachedAuthToken({token:access_token}, function() {
    //   console.log('OK removed');
    // });
    console.log(access_token);
    callback({access_token:access_token});
  });
}

function onGotAuthTokenSendToServer (access_token, callback) {
  console.log('onGotAuthTokenSendToServer');
  var xhr = new XMLHttpRequest();
  xhr.open('POST', zbBaseURL + zbAuthPath);
  xhr.setRequestHeader('Authorization', 'Bearer ' + access_token);
  xhr.onload = function(){
    onSendAccessTokenComplete(access_token, this.status, this.response, callback);
    retryConnection.release('onGotAuthTokenSendToServer'+access_token);
  };
  xhr.onerror = function(){
    retryConnection.release('onGotAuthTokenSendToServer'+access_token);
  }
  xhr.send();
}

function onSendAccessTokenComplete(access_token, status, response, callback) {
  console.log('onSendAccessTokenComplete ' + status + ' ' + response);
  if (status == 401) {
    chrome.identity.removeCachedAuthToken({ token: access_token });
    onUserInfoFetched('SendAuthTokenToServerError', status, response, callback);
  } else {
    onUserInfoFetched(null, status, response, callback);
  }
}

function onUserInfoFetched (error, status, response, callback) {
  console.log('onUserInfoFetched');
  if (!error && status == 200) {
    var user_info = JSON.parse(response);
    console.log(user_info);
    callback({status:status,user_info:user_info});
  } else {
    console.log({status:status,error:error});
    callback({status:status,error:error});
  }
}

function onGoogleAuthUnauthorized(callback) {
  console.log('onGoogleAuthUnauthorized');
  callback({error:true});
}
// Code updating the user interface, when the user information has been
// fetched or displaying the error.
/*
{
 "id": "115587419112044369619",
 "email": "sushi@zenblip.com",
 "verified_email": true,
 "name": "Shih-Wen Su",
 "given_name": "Shih-Wen",
 "family_name": "Su",
 "link": "https://plus.google.com/115587419112044369619",
 "picture": "https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg",
 "gender": "male",
 "hd": "zenblip.com"
}
*/

// var Messagelistener = function(){
//   chrome.runtime.onMessage.addListener(function(msg, msgSender, sendResponse){
//     console.log(msg);
//     console.log(msgSender);
//     console.log(sendResponse);
//   })
// }

var zenblip = (function(zb) {
  var zbBaseURL = 'https://zenblip.appspot.com';
  var ExtensionID = 'oocgfjghhllncddlnhlocnikogonjdcp';
  var authUserPath = '/auth/user';
  var current_user = null;
  var messenger = null;
  //var UKeys = []; //TODO: make it local

  /* messenger */
  zb.BackgroundMessenger = function(extensionID, messageHandler){
    this.extensionID = extensionID || ExtensionID;
    //this.port = chrome.runtime.connect(ExtensionID);
    // this.port.onDisconnect.addListener(function() {
    //   console.log('Messenger Disconnected');
    // });
    var self = this;
    chrome.runtime.onConnectExternal.addListener(function(port) {
      self.port = port;
      port.onMessage.addListener(function(msg) {
        messageHandler(msg, port);
      });
      port.onDisconnect.addListener(function() {
        console.log('onConnectExternal Messenger Disconnected');
      });
    });
  };

  zb.BackgroundMessenger.prototype.repost = function(origMsg, data){
    console.log('repost');
    if(origMsg.senderID){
      data.senderID = origMsg.senderID;
    }
    this.port.postMessage(data);
  };

  var backgroundMessageHandler = function(msg, port) {
    console.log('backgroundMessageHandler');
    console.log(msg);
    switch(msg.e){
      // case 'UserInit':
      //   console.log('UserInit');
      //   $.getJSON(zbBaseURL + authUserPath, function(result) {
      //     console.log(result);
      //     if(!result.error){
      //       messenger.repost(msg, {e:'GotUser', data:result});
      //     }else{
      //       messenger.repost(msg, {e:'GotUser', error:true});
      //     }
      //   });
      //   break;

      case 'getAndUpdateUserInfo':
        console.log('getAndUpdateUserInfo');
        getAndUpdateUserInfo(msg.options, function(result) {
          if(!result.error){
            messenger.repost(msg, {e:'GotUser', data:result.user_info});
          }else{
            messenger.repost(msg, {e:'GotUser', error:true});
          }
        });
        break;

      case 'SenderInit':

        //TODO: could be more accruate to match the tab id
        if(UKeys.indexOf(msg.ukey) == -1){
          UKeys.push(msg.ukey);
        }
        break;
      default:
        console.log('switch onConnectExternal Error');
        break;
    }
  };

  /* methods waiting to be sorted out... */

  zb.InitBackground = function(){
    console.log('Init');
    messenger = new zb.BackgroundMessenger(ExtensionID, backgroundMessageHandler, null);
  };
  return zb;
}(zenblip || {}));
zenblip.InitBackground();

