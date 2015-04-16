/**** zenblip Module *****/
var zenblip = (function(zb, $, Gmail) {
  // console.log(zb);

  var ExtensionID = 'oocgfjghhllncddlnhlocnikogonjdcp';
  var zbBaseURL = 'https://zenblip.appspot.com';
  var zbMainURL = 'https://www.zenblip.com';
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
  var composeIDs = [];
  // var debugCounter = 0;
  var zenblipAccessToken = '';
  var zbRedirectPath = '/l';
  var zbSignalPath = '/s';
  var zbTmpToken = '$$$zbTmpToken$$$';

  zb.trackStateName = zb.trackStateName || 'zb-track-state';
  zb.composedToolBoxData = zb.composedToolBoxData || 'zb-post-data';


  /* user */
  zb.User = function(email) {
    this.email = email;
    this.ukey = zb.hashFnv32a(email, true);
  };

  var contentMessageHandler = function(msg) {
    //
    // not used
    //
    // console.log('contentMessageHandler');
    // console.log(msg);
    if(msg.senderEmail != senderEmail){
      // console.log('Not my message');
      return;
    }
    switch(msg.e){
      // case 'GotUser':
      //   break;
      default:
        // console.log('Messenger default Error');
        break;
    }
  };

  zb.watchCompose = function(callback) {
    console.log('watchCompose');
    setInterval(function(){
      if(composeIDs !== zb.Gmail.get.compose_ids()){
        composeIDs = zb.Gmail.get.compose_ids();
        // console.log(composeIDs);
        callback(composeIDs);
      }
    }, 1000);
  };

  zb.attachSignal = function(body, token) {
    // return body + "<img src='http://www.needclickers.com/static/images/blessjewel0.gif?how=aboutthis' width='1' height='1' style='display:none'>";
    return body + "<div style='float:right'><img src='" + zbExternalURL + zbSignalPath + "/s.gif?u=" + sender.ukey + "&amp;t="+ token +"' width='0' height='0' style='display:none;opacity:0'></div>";
  };


  // zb.attachTrackCheckbox = function(options){
  //   var trackByDefault = options.track_by_default;
  //   var trackInput = "<input class='zbTrack' type='checkbox'>";
  //   if(trackByDefault){
  //     trackInput = "<input class='zbTrack' type='checkbox' checked>";
  //   }
  //   var $track = $("<span>"+trackInput+" Track</span>").css({
  //     'float': 'right',
  //     'font-size': '13px',
  //     'display': 'block',
  //     'height': '30px',
  //     'margin-top': '11px',
  //     'white-space': 'nowrap',
  //     'color': '#444',
  //   });
  //   var $hiddenInput = $("<input type='hidden' name='zbTrack'>");
  //   if(trackByDefault){
  //     $hiddenInput.val('1');
  //   }
  //   var $newMails = $('.aoI').not('.zbTracked').addClass('zbTracked');
  //   // console.log('$newMails '+ $newMails.length + ' '+debugCounter);
  //   //debugCounter++;
  //   //var zbEmailID;
  //   var $this;
  //   $newMails.each(function(index){
  //     //console.log('index ' + index);
  //     $this = $(this);
  //     //zbEmailID = $this.attr('zbEmailID');
  //     //if(zbEmailID !== undefined){
  //     //  continue;
  //     //}
  //     var $thisHiddenInput = $hiddenInput.clone();
  //     $thisTrack = $track.clone();
  //     $thisTrack.find('input').change(function(){
  //       $thisHiddenInput.val(this.checked ? "1":"0");
  //       console.log('checkbox changed ' + $thisHiddenInput.val());
  //       //change send button
  //       if(this.checked === true){
  //         console.log('checked');
  //         $this.find('.aoO').attr('data-tooltip', 'Send ‪and Track')
  //           .addClass('tracked-send-buton');
  //       }else{
  //         console.log('unchecked');
  //         $this.find('.aoO').attr('data-tooltip', 'Send ‪without tracking?')
  //           .removeClass('tracked-send-buton');
  //       }
  //     });
  //     //zbEmailID = zb.uuid().replace(/-/g,'').substr(-20);

  //     //Init state
  //     $this
  //       //.attr('zbEmailID', zbEmailID)
  //       .find('form').append($thisHiddenInput)
  //       // .find('form').append("<input type='hidden' name='zbEmailID' value='"+zbEmailID+"'>")
  //       .end().find('.aWQ').prepend($thisTrack)
  //       // .end().find('.aoO').attr('data-tooltip', 'Send ‪without tracking? (⌘Enter)')
  //       .end().find('.aWR').css('display', 'none')
  //       .end().find('.oG').css('display', 'none');
  //     if(trackByDefault){
  //       $this.find('.aoO').addClass('tracked-send-buton').attr('data-tooltip', 'Send ‪and Track');
  //     }
  //   });
  // };
  zb.addBeacon = function(bps, composedToolBoxData) {
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
    //console.log(bps);
    var links, payload,
      token = zb.uuid().replace(/-/g,'').substr(-20);
      version = typeof zbExtDetails == 'undefined'? '': zbExtDetails.version;
    var trackState = composedToolBoxData.track_state == "1"? true:false;
    try {
      links = zb.parseLink(bps.body, zbExternalURL);
      //TODO: move this script to tracker domain and add csrf token
      payload = {
        version: version,
        client: "gmail",
        cc: bps.cc ? bps.cc.join(',') : "",
        bcc: bps.bcc ? bps.bcc.join(',') : "",
        to: bps.to ? bps.to.join(',') : "",
        sender: zb.Gmail.get.user_email(),
        subject: bps.subject,
        links: JSON.stringify(links),
        token:token,
        access_token: zenblipAccessToken,
        tz_offset:(new Date()).getTimezoneOffset()/-60,
        track_state: trackState
      };
      for(var k in composedToolBoxData){
        payload[k] = composedToolBoxData[k];
      }
      //console.log(payload);
    } catch (err) {
      console.log(err);
    }

    if(trackState){
      var bodyDecoded = zb.replaceLinks(bps.body, token, links, sender.ukey, zbExternalURL, zbRedirectPath);
      bodyWithSignal = zb.attachSignal(bodyDecoded, token);
      return {'body':bodyWithSignal, 'payload':payload};
    }else{
      return {'body':bps.body, 'payload':payload};
    }
  };
  zb.sendBeaconToServer = function(payload){
    console.log("sendBeaconToServer");
    var registerID = 'sendBeaconToServer_'+ zb.uuid();
    zb.retryConnection.hold(registerID, 30*1000, function() {
      zb.sendBeaconToServer(payload);
    });
    $.post(zbBaseURL + '/signals/add?sync=1', payload, function(jdata) {
      //console.log(jdata);
      zb.retryConnection.release(registerID);
    });
  };
  zb.emailBeforeSend = function(url, body, data, xhr) {
    var bps = xhr.xhrParams.body_params;
    var mid = bps.mid;
    var $mail = $('.' + mid);
    var composedToolBoxData = $mail.data(zb.composedToolBoxData);
    //console.log('track this email');
    var result = zb.addBeacon(bps, composedToolBoxData);
    if(typeof result.error != undefined){
      bps.body = result.body;
      zb.sendBeaconToServer(result.payload);
    }
  };

  zb.ChannelInit = function() {
    var options = {
      isCreate: false, 
      senderEmail:sender.email,
      uri: zbBaseURL + zbChannelPath
    };
    //def in channel.js
    zb.getOrCreateChannelToken(options, function() {
      zb.openChannel(options);
    });
  };

  zb.TrackerInit = function(options) {
    //applied when user authorized
    console.log('TrackerInit');
    zenblipAccessToken = options.zenblipAccessToken;
    zb.Gmail.observe.before('send_message', zb.emailBeforeSend);
    zb.watchCompose(function() {
      // zb.attachTrackCheckbox({track_by_default:options.track_by_default});
      zb.addComposeToolBoxToComposingMails({track_by_default:options.track_by_default});
    });
    zb.ChannelInit();
  };

  zb.SenderInit = function(){
    console.log('zenblip sender init');
    zb.Gmail = new Gmail();
    sender = new zb.User(zb.Gmail.get.user_email());
    senderID = sender.email;
    messenger = new zb.Messenger(ExtensionID, contentMessageHandler, sender);
    messenger.post({'e':'SenderInit','senderEmail':sender.email,'ukey':sender.ukey});
    document.dispatchEvent(new CustomEvent('zbInit', {
      detail:{e:'zbInit',
      sender:sender,
      senderEmail:sender.email,
    }
    }));
  };
  return zb;
}(zenblip || {}, jQuery, Gmail));

window.addEventListener("message", function(e) {
  if (e.source != window){
    return;
  }
  if(e.data && typeof e.data.type != 'undefined'){
    switch(e.data.type){
      case 'zbTrackerInit':
        zenblip.TrackerInit(e.data);
        break;
      default:
        break;
    }
  }
});

function launch() {
  console.log('launch');
  if (typeof goog == 'undefined') {
    setTimeout(function() {
      console.log('setTimeout launch');
      launch();
    }, 100);
  } else {
    zenblip.SenderInit();
  }
}
launch();
