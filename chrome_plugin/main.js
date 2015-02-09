//TODO: module pattern

// var zbBaseURL = 'http://127.0.0.1:8888',
// var zbBaseURL = 'https://zenblip.appspot.com';
// var zbExternalURL = 'http://www.email-link.com';
// var signalResourcePath = '/resource/signals';
// var linkResourcePath = '/resource/links';
// var zbRedirectPath = '/l',
//   zbSignalPath = '/s',
//   zbTmpToken = '$$$zbTmpToken$$$',
//   zbGmail,
//   zbSender,
//   zbUKey;
// zbBaseURL = 'https://zenblip.appspot.com',



// var refresh = function(f) {
//   if (/in/.test(document.readyState)) {
//     setTimeout('refresh(' + f + ')', 10);
//   } else {
//     f();
//   }
// };

// var decodeBody = function(body) {
//   return body.replace('<wbr>', ''); //TODO: WTF?
// };

// var parseLink = function(body) {
//   var urlPack = function(url, plain) {
//     var urlDecoded,
//       urlHash;
//     urlDecoded = url.replace(/&amp;/g, '&'); //TODO:improve this if necessary
//     urlHash = hashCode(urlDecoded);
//     return {
//       url: url,
//       urlDecoded: urlDecoded,
//       urlHash: urlHash,
//       plain: plain
//     };
//   };
//   console.log('parseLink');
//   try {
//     var linkRegexWithATag = /<[Aa][^<>]* [Hh][Rr][Ee][Ff]=[\"\']([Hh][Tt][Tt][Pp][Ss]?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:;%_\+.~#?&//=]*))[\"\'].*?>.*?<\/[Aa]>/g; //"
//     var linkRegexInPlainText = /[Hh][Tt][Tt][Pp][Ss]?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:;%_\+.~#?&//=]*)/g,
//       bodyDecoded = decodeBody(body),
//       links = [],
//       plainLinks = [],
//       linksDecoded = [],
//       plainLinksDecoded = [];
//     //deal with links with html A tag
//     var match = linkRegexWithATag.exec(bodyDecoded);
//     while (match != null) {
//       links.push(urlPack(match[1], 0));
//       match = linkRegexWithATag.exec(bodyDecoded);
//     }

//     //deal with plain url link
//     var bodyDecoded2 = bodyDecoded.replace(linkRegexWithATag, '');

//     plainLinks = bodyDecoded2.match(linkRegexInPlainText);
//     if (plainLinks != null && plainLinks.length > 0) {
//       for (var i = plainLinks.length; i--;) {
//         links.push(urlPack(plainLinks[i], 1));
//       }
//     }

//     //
//     // if(links.length > 0){
//     // for(var i=links.length; i--;){
//     // linksDecoded.push(links[i].replace(/&amp;/g,'&'));
//     // }
//     // }

//     console.log(links);
//     // bodyDecoded = bodyDecoded.replace(url, zbBaseURL + zbRedirectPath + '?t=' + zbTmpToken +'&h=' +urlHash);
//     return links;
//   } catch (e) {
//     console.log(e);
//   }
// };

// var replaceLinks = function(body, token, links) {
//   var bodyDecoded = decodeBody(body),
//     tag, l, newURL;

//   console.log('replaceLinks');
//   for (var i = 0; i < links.length; i++) { //order sequence matters
//     l = links[i];
//     newURL = zbExternalURL + zbRedirectPath + "?u=" + zbUKey + "&amp;t=" + token + "&amp;h=" + l.urlHash;
//     if (l.plain === 1) {
//       //if plain, convert to html tag
//       newURL = "<a href='" + newURL + "'>" + l.urlDecoded + "</a>";
//     }
//     bodyDecoded = bodyDecoded.replace(l.url, newURL);
//   }
//   return bodyDecoded;
// };

// var attachSignal = function(body, token) {
//   // return body + "<img src='http://www.needclickers.com/static/images/blessjewel0.gif?how=aboutthis' width='1' height='1' style='display:none'>";
//   return body + "<img src='" + zbExternalURL + zbSignalPath + "/s.gif?u=" + zbUKey + "&amp;t="+ token +"' width='1' height='1' style='display:none'>";
// };

// var addBeacon = function(bps) {
//   /*
//   body_params:
//   {
//   bcc:["bcc@ex.com"],
//   cc:["cc@ex.com",""],
//   body:"<div dir="ltr">t_body<br clear="all"></div>",
//   composeid:"1408469390659",
//   draft:"147ef5283179e4e7",
//   from:"from@ex.com",
//   ishtml:1,
//   subject:"subject",
//   to:[""Su" <to@ex.com>"],
//   }
//   */
//   //TODO: we can use compose id
//   if (!bps.ishtml) {
//     return {'error':'NotHTML'};
//   }

//   var links, payload,
//     token = uuid().replace(/-/g,'').substr(-20);
//     version = typeof zbExtDetails == 'undefined'? '': zbExtDetails.version;
//   try {
//     links = parseLink(bps.body);
//     payload = {
//       version: version,
//       cc: bps.cc ? bps.cc.join(',') : "",
//       bcc: bps.bcc ? bps.bcc.join(',') : "",
//       to: bps.to ? bps.to.join(',') : "",
//       sender: zbGmail.get.user_email(),
//       subject: bps.subject,
//       links: JSON.stringify(links),
//       token:token,
//       tz_offset:(new Date()).getTimezoneOffset()/-60,
//       csrf_token: getCookie('_csrf_token')
//     };
//     console.log(payload);
//   } catch (err) {
//     console.log(err);
//   }

//   var bodyDecoded = replaceLinks(bps.body, token, links);
//   bodyWithSignal = attachSignal(bodyDecoded, token);
//   return {'body':bodyWithSignal,
//       'payload':payload};
// };

// var sendBeaconToServer = function(payload){
//   console.log("sendBeaconToServer");
//   var registerID = 'sendBeaconToServer_'+uuid();
//   zbUtils.retryConnection.hold(registerID, 30*1000, function() {
//     sendBeaconToServer(payload);
//   });
//   $.post(zbBaseURL + '/signals/add?sync=1', payload, function(jdata) {
//     console.log(jdata);
//     zbUtils.retryConnection.release(registerID);
//   });
// };

//======================================================================


// var debugCounter = 0;
// var attachTrackCheckbox = function(){
//   var $track = $("<span><input class='zbTrack' type='checkbox' checked> Track</span>").css({
//     'float': 'right',
//     'font-size': '13px',
//     'display': 'block',
//     'height': '30px',
//     'margin-top': '11px',
//     'white-space': 'nowrap',
//     'color': '#444',
//   });
//   var $hiddenInput = $("<input type='hidden' name='zbTrack' value='1'>");
//   var $newMails = $('.aoI').not('.zbTracked').addClass('zbTracked');
//   // console.log('$newMails '+ $newMails.length + ' '+debugCounter);
//   debugCounter++;
//   var zbEmailID, $this;
//   $newMails.each(function(index){
//     console.log('index ' + index);
//     $this = $(this);
//     zbEmailID = $this.attr('zbEmailID');
//     if(zbEmailID === undefined){
//       $thisHiddenInput = $hiddenInput.clone();
//       $thisTrack = $track.clone();
//       $thisTrack.find('input').change(function(){
//         $thisHiddenInput.val(this.checked ? "1":"0");
//         console.log('checkbox changed ' + $thisHiddenInput.val());
//         //change send button
//         if(this.checked === true){
//           console.log('checked');
//           $this.find('.aoO').attr('data-tooltip', 'Send ‪and Track')
//             .addClass('tracked-send-buton');
//         }else{
//           console.log('unchecked');
//           $this.find('.aoO').attr('data-tooltip', 'Send ‪without tracking?')
//             .removeClass('tracked-send-buton');
//         }
//       });
//       zbEmailID = uuid().replace(/-/g,'').substr(-20);

//       //Init state
//       $this.attr('abEmailID', zbEmailID)
//         .find('form').append($thisHiddenInput)
//         // .find('form').append("<input type='hidden' name='zbEmailID' value='"+zbEmailID+"'>")
//         .end().find('.aWQ').prepend($thisTrack)
//         // .end().find('.aoO').attr('data-tooltip', 'Send ‪without tracking? (⌘Enter)')
//         .end().find('.aoO').attr('data-tooltip', 'Send ‪and Track').addClass('tracked-send-buton')
//         .end().find('.aWR').css('display', 'none')
//         .end().find('.oG').css('display', 'none');
//     }
//   });
// };




//function onNewMail(id, url, body, xhr) {
  //console.log("id:", id, "url:", url, 'body', body, 'xhr', xhr);
//};




//var main = function() {
  //zbGmail = new Gmail();
  //console.log('Hello again,', zbGmail.get.user_email());

  //remove this
  //document.body.setAttribute('zbSender', zbGmail.get.user_email());

  //zbSender = zbGmail.get.user_email(); //d
  //zbUKey = hashFnv32a(zbSender, true) //d

  //document.dispatchEvent(new CustomEvent('zbSenderInit', {
  //  detail:{'e':'zbSenderInit','sender':zbSender,'ukey':zbUKey}
  //}));
  //channel
  
  //TODO: move to zb module
  // getOrCreateToken(openChannel);
  // watchCompose(attachTrackCheckbox);

  // zbGmail.observe.before('send_message', function(url, body, data, xhr) {
  //   var bps = xhr.xhrParams.body_params;
  //   console.log(bps);
  //   console.log(bps.zbTrack);
  //   if(bps.zbTrack === "1"){
  //     console.log('track this email');
  //     var result = addBeacon(bps);
  //     if(typeof result.error != undefined){
  //       bps.body = result.body;
  //       sendBeaconToServer(result.payload);
  //     }
  //   }
  // });
  //zbGmail.observe.on("new_email", onNewMail);
  // zbGmail.observe.before("open_email", function(id, url, body, xhr) {
  //   console.log('before open_email');
  //   console.log("id:", id, "url:", url, 'body', body, 'xhr', xhr);
  //   console.log(zbGmail.get.email_data(id));
  //   var me = zbGmail.get.user_email();
  //   var g = zbGmail.get.email_data(id);


  //   for( var key in g.threads){
  //     if(g.threads.hasOwnProperty(key)){
  //       var email = g.threads[key];
  //       if(email.from_email == me){
  //         // console.log('OOOOOOOOOOO');
  //         // zbGmail.get.email_data(id).threads[key].content_html = \
  //         // email.content_html.replace(/\<img.*?\/s\/s\.gif.*?\>/,'');
  //       }
  //     }
  //   }
  // });
//};



/**** zenblip Module *****/
var zenblip = (function(zb, $, Gmail, React) {
  console.log(zb);

  var ExtensionID = 'oocgfjghhllncddlnhlocnikogonjdcp';
  var zbBaseURL = 'https://zenblip.appspot.com';
  var zbExternalURL = 'http://www.email-link.com';
  var zbChannelPath = '/channels/';
  var signalResourcePath = '/resource/signals';
  var linkResourcePath = '/resource/links';
  var authUserPath = '/auth/user';
  var current_user = null;
  var gmail = null;
  var sender = null;
  var senderID;
  var messenger;
  var raDashboard;
  var composeIDs = [];
  var debugCounter = 0;
  var zbRedirectPath = '/l',
    zbSignalPath = '/s',
    zbTmpToken = '$$$zbTmpToken$$$';
  /* user */
  zb.User = function(email) {
    this.email = email;
    this.ukey = zb.hashFnv32a(email, true);
  };

  /* messenger */
  zb.Messenger = function(extensionID, messageHandler, sender){
    this.extensionID = extensionID || ExtensionID;
    this.sender = sender;
    this.port = chrome.runtime.connect(ExtensionID);
    this.port.onMessage.addListener(messageHandler);
    this.port.onDisconnect.addListener(function() {
      console.log('Messenger Disconnected');
    });
  };

  zb.Messenger.prototype.post = function(data){
    if(senderID){
      data.senderID = senderID;
    }
    this.port.postMessage(data);
  };

  var contentMessageHandler = function(msg) {
    console.log('contentMessageHandler');
    console.log(msg);
    if(msg.senderID != senderID){
      console.log('Not my message');
      return;
    }
    switch(msg.e){
      case 'GotUser':
        //TODO: login dashboard
        if(!msg.error){
          raDashboard.onAuthenticated({senderEmail:sender.email});
          if(!zb._trackerInitialized){
            zb.trackerInit();
          }
          zb.ChannelInit();
        }else{
          raDashboard.onAuthenticationFailed();
          console.log('GotUser Error');
        }
        break;
      default:
        console.log('Messenger default Error');
        break;
    }
  };

  /*** end of messenger **/


  zb.watchCompose = function(callback) {
    console.log('watchCompose');
    setInterval(function(){
      if(composeIDs !== zb.Gmail.get.compose_ids()){
        composeIDs = zb.Gmail.get.compose_ids();
        // console.log(composeIDs);
        callback(composeIDs);
      }
    }, 2000);
  };
  zb.decodeBody = function(body) {
    return body.replace('<wbr>', ''); //TODO: WTF?
  };

  zb.parseLink = function(body) {
    var urlPack = function(url, plain) {
      var urlDecoded,
        urlHash;
      urlDecoded = url.replace(/&amp;/g, '&'); //TODO:improve this if necessary
      urlHash = zb.hashCode(urlDecoded);
      return {
        url: url,
        urlDecoded: urlDecoded,
        urlHash: urlHash,
        plain: plain
      };
    };
    console.log('parseLink');
    try {
      var linkRegexWithATag = /<[Aa][^<>]* [Hh][Rr][Ee][Ff]=[\"\']([Hh][Tt][Tt][Pp][Ss]?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:;%_\+.~#?&//=]*))[\"\'].*?>.*?<\/[Aa]>/g; //"
      var linkRegexInPlainText = /[Hh][Tt][Tt][Pp][Ss]?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:;%_\+.~#?&//=]*)/g,
        bodyDecoded = zb.decodeBody(body),
        links = [],
        plainLinks = [],
        linksDecoded = [],
        plainLinksDecoded = [];
      //deal with links with html A tag
      var match = linkRegexWithATag.exec(bodyDecoded);
      while (match != null) {
        links.push(urlPack(match[1], 0));
        match = linkRegexWithATag.exec(bodyDecoded);
      }

      //deal with plain url link
      var bodyDecoded2 = bodyDecoded.replace(linkRegexWithATag, '');

      plainLinks = bodyDecoded2.match(linkRegexInPlainText);
      if (plainLinks != null && plainLinks.length > 0) {
        for (var i = plainLinks.length; i--;) {
          links.push(urlPack(plainLinks[i], 1));
        }
      }

      console.log(links);
      // bodyDecoded = bodyDecoded.replace(url, zbBaseURL + zbRedirectPath + '?t=' + zbTmpToken +'&h=' +urlHash);
      return links;
    } catch (e) {
      console.log(e);
    }
  };

  zb.replaceLinks = function(body, token, links) {
    var bodyDecoded = zb.decodeBody(body),
      tag, l, newURL;

    console.log('replaceLinks');
    for (var i = 0; i < links.length; i++) { //order sequence matters
      l = links[i];
      newURL = zbExternalURL + zbRedirectPath + "?u=" + sender.ukey + "&amp;t=" + token + "&amp;h=" + l.urlHash;
      if (l.plain === 1) {
        //if plain, convert to html tag
        newURL = "<a href='" + newURL + "'>" + l.urlDecoded + "</a>";
      }
      bodyDecoded = bodyDecoded.replace(l.url, newURL);
    }
    return bodyDecoded;
  };

  zb.attachSignal = function(body, token) {
    // return body + "<img src='http://www.needclickers.com/static/images/blessjewel0.gif?how=aboutthis' width='1' height='1' style='display:none'>";
    return body + "<img src='" + zbExternalURL + zbSignalPath + "/s.gif?u=" + sender.ukey + "&amp;t="+ token +"' width='1' height='1' style='display:none'>";
  };
  zb.attachTrackCheckbox = function(){
    var $track = $("<span><input class='zbTrack' type='checkbox' checked> Track</span>").css({
      'float': 'right',
      'font-size': '13px',
      'display': 'block',
      'height': '30px',
      'margin-top': '11px',
      'white-space': 'nowrap',
      'color': '#444',
    });
    var $hiddenInput = $("<input type='hidden' name='zbTrack' value='1'>");
    var $newMails = $('.aoI').not('.zbTracked').addClass('zbTracked');
    // console.log('$newMails '+ $newMails.length + ' '+debugCounter);
    debugCounter++;
    var zbEmailID, $this;
    $newMails.each(function(index){
      console.log('index ' + index);
      $this = $(this);
      zbEmailID = $this.attr('zbEmailID');
      if(zbEmailID === undefined){
        $thisHiddenInput = $hiddenInput.clone();
        $thisTrack = $track.clone();
        $thisTrack.find('input').change(function(){
          $thisHiddenInput.val(this.checked ? "1":"0");
          console.log('checkbox changed ' + $thisHiddenInput.val());
          //change send button
          if(this.checked === true){
            console.log('checked');
            $this.find('.aoO').attr('data-tooltip', 'Send ‪and Track')
              .addClass('tracked-send-buton');
          }else{
            console.log('unchecked');
            $this.find('.aoO').attr('data-tooltip', 'Send ‪without tracking?')
              .removeClass('tracked-send-buton');
          }
        });
        zbEmailID = zb.uuid().replace(/-/g,'').substr(-20);

        //Init state
        $this.attr('abEmailID', zbEmailID)
          .find('form').append($thisHiddenInput)
          // .find('form').append("<input type='hidden' name='zbEmailID' value='"+zbEmailID+"'>")
          .end().find('.aWQ').prepend($thisTrack)
          // .end().find('.aoO').attr('data-tooltip', 'Send ‪without tracking? (⌘Enter)')
          .end().find('.aoO').attr('data-tooltip', 'Send ‪and Track').addClass('tracked-send-buton')
          .end().find('.aWR').css('display', 'none')
          .end().find('.oG').css('display', 'none');
      }
    });
  };
  zb.addBeacon = function(bps) {
    /*
    body_params:
    {
    bcc:["bcc@ex.com"],
    cc:["cc@ex.com",""],
    body:"<div dir="ltr">t_body<br clear="all"></div>",
    composeid:"1408469390659",
    draft:"147ef5283179e4e7",
    from:"from@ex.com",
    ishtml:1,
    subject:"subject",
    to:[""Su" <to@ex.com>"],
    }
    */
    //TODO: we can use compose id
    if (!bps.ishtml) {
      return {'error':'NotHTML'};
    }

    var links, payload,
      token = zb.uuid().replace(/-/g,'').substr(-20);
      version = typeof zbExtDetails == 'undefined'? '': zbExtDetails.version;
    try {
      links = zb.parseLink(bps.body);
      payload = {
        version: version,
        cc: bps.cc ? bps.cc.join(',') : "",
        bcc: bps.bcc ? bps.bcc.join(',') : "",
        to: bps.to ? bps.to.join(',') : "",
        sender: zb.Gmail.get.user_email(),
        subject: bps.subject,
        links: JSON.stringify(links),
        token:token,
        tz_offset:(new Date()).getTimezoneOffset()/-60
      };
      console.log(payload);
    } catch (err) {
      console.log(err);
    }

    var bodyDecoded = zb.replaceLinks(bps.body, token, links);
    bodyWithSignal = zb.attachSignal(bodyDecoded, token);
    return {'body':bodyWithSignal,
        'payload':payload};
  };
  zb.sendBeaconToServer = function(payload){
    console.log("sendBeaconToServer");
    var registerID = 'sendBeaconToServer_'+ zb.uuid();
    zb.retryConnection.hold(registerID, 30*1000, function() {
      zb.sendBeaconToServer(payload);
    });
    $.post(zbBaseURL + '/signals/add?sync=1', payload, function(jdata) {
      console.log(jdata);
      zb.retryConnection.release(registerID);
    });
  };
  zb.emailBeforeSend = function(url, body, data, xhr) {
    var bps = xhr.xhrParams.body_params;
    if(bps.zbTrack === "1"){
      console.log('track this email');
      var result = zb.addBeacon(bps);
      if(typeof result.error != undefined){
        bps.body = result.body;
        zb.sendBeaconToServer(result.payload);
      }
    }
  };

  zb.trackerInit = function() {
    zb.Gmail.observe.before('send_message', zb.emailBeforeSend);
    zb.watchCompose(zb.attachTrackCheckbox);
    zb._trackerInitialized = true;
  };

  zb.ChannelInit = function() {
    var options = {
      isCreate: false, 
      senderEmail:sender.email,
      uri: zbBaseURL + zbChannelPath
    };
    zb.getOrCreateChannelToken(options, function() {
      zb.openChannel(options);
    });
  };
  zb.UserInit = function() {
    zb.getAndUpdateUserInfo(false);
  };
  zb.SenderInit = function() {
    messenger.post({'e':'SenderInit','sender':sender.email,'ukey':sender.ukey})
  };
  zb.DashboardInit = function() {
    var dashboard = document.createElement('div');
    dashboard.id = 'zenblip-dashboard-container';
    $('div.nH.w-asV.aiw')[0].appendChild(dashboard);
    // zb.getElementByXpath("/html/body/div[7]/div[3]/div/div[1]").appendChild(dashboard);
    raDashboard = React.render(
      React.createElement(SignalApp, {senderEmail: sender.email, baseURL: zbBaseURL, 
        signalResourcePath: signalResourcePath, linkResourcePath: linkResourcePath}),
      document.getElementById(dashboard.id)
    );
  };


  /* methods waiting to be sorted out... */
  // zb.getAndUpdateUserInfo = function(interactive) {
  //   console.log('zb.getAndUpdateUserInfo');
  //   var options = {interactive:interactive}
  //   messenger.post({e:'getAndUpdateUserInfo', options:options});
  // };

  zb.getAndUpdateUserInfo = function(interactive) {
    //This function is used in dashboard.js
    console.log('zb.getAndUpdateUserInfo');
    var options = {interactive:interactive}
    messenger.post({e:'getAndUpdateUserInfo', options:options});
  };

  zb.Init = function(){
    console.log('zenblip init');
    zb.Gmail = new Gmail();
    sender = new zb.User(zb.Gmail.get.user_email());
    senderID = sender.email;
    messenger = new zb.Messenger(ExtensionID, contentMessageHandler, sender);
    zb.UserInit();
    zb.SenderInit();
    zb.DashboardInit();

  };
  return zb;
}(zenblip || {}, jQuery, Gmail, React));

function launch() {
  console.log('launch');
  if (typeof goog == 'undefined') {
    setTimeout(function() {
      console.log('setTimeout launch');
      launch();
    }, 100);
  } else {
    zenblip.Init();
  }
}
launch();