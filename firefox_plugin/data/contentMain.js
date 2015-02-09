//TODO: module pattern

// var zbBaseURL = 'http://127.0.0.1:8888',
var zbBaseURL = 'https://zenblip.appspot.com';
var zbExternalURL = 'http://www.email-link.com';
var zbRedirectPath = '/l',
    zbSignalPath = '/s',
    zbTmpToken = '$$$zbTmpToken$$$',
    zbGmail;

var uuid = function(){
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
        return v.toString(16);
    });
};
var hashCode = function(string) {
    var hash = 0;
    if (string.length === 0) return hash;
    for (i = 0; i < string.length; i++) {
        char = string.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash.toString();
};

var refresh = function(f) {
    if (/in/.test(document.readyState)) {
        setTimeout('refresh(' + f + ')', 10);
    } else {
        f();
    }
};

var decodeBody = function(body) {
    return body.replace('<wbr>', ''); //TODO: WTF?
};

var parseLink = function(body) {
    var urlPack = function(url, plain) {
        var urlDecoded,
            urlHash;
        urlDecoded = url.replace(/&amp;/g, '&'); //TODO:improve this if necessary
        urlHash = hashCode(urlDecoded);
        return {
            url: url,
            urlDecoded: urlDecoded,
            urlHash: urlHash,
            plain: plain
        };
    };
    console.log('parseLink');
    try {
        var linkRegexWithATag = /<[Aa][^<>]* [Hh][Rr][Ee][Ff]=[\"\']([Hh][Tt][Tt][Pp][Ss]?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:;%_\+.~#?&//=]*))[\"\'.*?>.*?<\/[Aa]>/g; //"
        var linkRegexInPlainText = /[Hh][Tt][Tt][Pp][Ss]?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:;%_\+.~#?&//=]*)/g,
            bodyDecoded = decodeBody(body),
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

        //
        // if(links.length > 0){
        // for(var i=links.length; i--;){
        // linksDecoded.push(links[i].replace(/&amp;/g,'&'));
        // }
        // }

        console.log(links);
        // bodyDecoded = bodyDecoded.replace(url, zbBaseURL + zbRedirectPath + '?t=' + zbTmpToken +'&h=' +urlHash);
        return links;
    } catch (e) {
        console.log(e);
    }
};

var replaceLinks = function(body, token, links) {
    var bodyDecoded = decodeBody(body),
        tag, l, newURL;

    console.log('replaceLinks');
    for (var i = 0; i < links.length; i++) { //order sequence matters
        l = links[i];
        newURL = zbExternalURL + zbRedirectPath + "?t=" + token + "&h=" + l.urlHash;
        if (l.plain === 1) {
            //if plain, convert to html tag
            newURL = "<a href='" + newURL + "'>" + l.urlDecoded + "</a>";
        }
        bodyDecoded = bodyDecoded.replace(l.url, newURL);
    }
    return bodyDecoded;
};

var attachSignal = function(body, token) {
    // return body + "<img src='http://www.needclickers.com/static/images/blessjewel0.gif?how=aboutthis' width='1' height='1' style='display:none'>";
    return body + "<img src='" + zbExternalURL + zbSignalPath + "/s.gif?t="+ token +"' width='1' height='1' style='display:none'>";
};

var addBeacon = function(bps) {
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
    console.log("OK1");
    console.log(bps);
    if (!bps.ishtml) {
        return {'error':'NotHTML'};
    }

    var links, payload,
        token = uuid().replace(/-/g,'').substr(-20);
    try {
        links = parseLink(bps.body);
        payload = {
            cc: bps.cc ? bps.cc.join(',') : "",
            bcc: bps.bcc ? bps.bcc.join(',') : "",
            to: bps.to ? bps.to.join(',') : "",
            sender: zbGmail.get.user_email(),
            subject: bps.subject,
            links: JSON.stringify(links),
            token:token,
            tz_offset:(new Date()).getTimezoneOffset()/-60
        };
        console.log(payload);
    } catch (err) {
        console.log(err);
    }

    console.log("OK2");
    var bodyDecoded = replaceLinks(bps.body, token, links);
    bodyWithSignal = attachSignal(bodyDecoded, token);
    return {'body':bodyWithSignal,
            'payload':payload};
};

var sendBeaconToServer = function(payload){
    console.log("sendBeaconToServer");
    $.post(zbBaseURL + '/signals/add?sync=1', payload, function(jdata) {
        console.log(jdata);
    });
};

//======================================================================
var channelToken,
    _renewTimer = 60*60*1000, //renew per hour(google times out per 2 hour)
    _initTimer = 1*1000, //1 second
    timerCount = _initTimer,
    userInfo = null;

var xhRequest = function(method, url, callback){
    var xhr;
    if(window.XMLHttpRequest){
        xhr = new XMLHttpRequest();
    }else{
        //IE5, 6, maybe we don't need to support this
        xhr = new ActiveXObject("Microsoft.XMLHTTP");
    }
    xhr.onreadystatechange = function(){
        if(xhr.readyState == xhr.DONE){
            if(xhr.status == 200){
                callback(xhr.responseText);
            }else{
                console.log("xhr Error 1");
            }
        }
    };
    xhr.open(method, url, true);
    xhr.send(null);
};

var performing = false;
var performGetOrCreateToken = function(){
    console.log('performGetOrCreateToken');
    if(!performing){
        setTimeout(function(){
            console.log('setTimeout performGetOrCreateToken');
            performing = false;
            getOrCreateToken(openChannel, true);
        }, timerCount);
        console.log('reconnect after ' + timerCount/1000 +' seconds');
        timerCount = Math.pow(timerCount, 2);
        performing = true;
    }
};
var getOrCreateToken = function(callback, isCreate){
    /* JSON.parse browser support:
     Feature    Chrome  Firefox (Gecko) Internet Explorer   Opera   Safari
     Basic support(Yes)   3.5 (1.9.1)    8.0                 10.5    4.0
    * */
    console.log('getOrCreateToken');
    var path = isCreate? "create_token":"get_token";
    $.post(zbBaseURL + "/channels/"+path, {owner:zbGmail.get.user_email()}, function(jdata){
        console.log('got channel token');
        console.log(jdata);
        if(jdata.error){
            console.log(jdata.error);
            performGetOrCreateToken();
            callback();
        }else{
            channelToken = jdata.channel_token;
            timerCount = 1000;
            callback();
        }
    });
};
var onOpened = function() {
    connected = true;
   // sendMessage('opened');
    console.log("opened");
    setTimeout(function(){
        getOrCreateToken(openChannel, true);
    }, _renewTimer);
    timerCount = _initTimer;
};
var onMessage2 = function(jmsg) {
    console.log('onMessage');
    console.log(jmsg);
    // chrome.runtime.sendMessage({msg:jmsg});
    document.dispatchEvent(new CustomEvent('zbNotificationMessage', {
        detail:jmsg
    }));
    // $(document.body).data('zbMsg', jmsg);
    // $("#messages ul").append($("<li></li>").html(msg.data));

};
var onError = function(err) {
    console.log("Got error");
    console.log(err);
    if(err && err.code == 401){
        performGetOrCreateToken();
    }
};
var onClose = function() {
   // alert("close");
 //   connected = false;
    console.log("close");
};
// open new session
var openChannel = function(){
    console.log('openChannel: ' + channelToken);
    var channel = new goog.appengine.Channel(channelToken);
    var socket = channel.open();
    socket.onopen = onOpened;
    socket.onmessage = onMessage2;
    socket.onerror = onError;
    socket.onclose = onClose;
};


// var registerTab = function(){
//     console.log(chrome);
//     console.log(chrome.extension);
//     console.log(chrome.runtime);
//     chrome.extension.sendMessage({action:'register'}); //chrome.extension undefined
//     chrome.runtime.sendMessage({action:'register'}); //chrome.runtime undefined
// }

var debugCounter = 0;
var attachTrackCheckbox = function(){
    var $track = $("<span><input class='zbTrack' type='checkbox'> Track</span>").css({
        'float': 'right',
        'font-size': '14px',
        'display': 'block',
        'height': '30px',
        'margin-top': '11px',
        'margin-left': '5px',
        'color': '#444',
    });
    var $hiddenInput = $("<input type='hidden' name='zbTrack' value='0'>");
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
                    $this.find('.aoO').attr('data-tooltip', 'Send ‪and Track (⌘Enter)')
                        .addClass('tracked-send-buton');
                }else{
                    console.log('unchecked');
                    $this.find('.aoO').attr('data-tooltip', 'Send ‪without tracking? (⌘Enter)')
                        .removeClass('tracked-send-buton');
                }
            });
            zbEmailID = uuid().replace(/-/g,'').substr(-20);
            $this.attr('abEmailID', zbEmailID)
                .find('form').append($thisHiddenInput)
                // .find('form').append("<input type='hidden' name='zbEmailID' value='"+zbEmailID+"'>")
                .end().find('.aWQ').prepend($thisTrack)
                .end().find('.aoO').attr('data-tooltip', 'Send ‪without tracking? (⌘Enter)');
        }
    });
};

var composeIDs = [];
var watchCompose = function(callback){
    console.log('watchCompose');
    setInterval(function(){
        if(composeIDs !== zbGmail.get.compose_ids()){
            composeIDs = zbGmail.get.compose_ids();
            // console.log(composeIDs);
            callback(composeIDs);
        }
    }, 2000);
};

var main = function() {
    console.log('Main starts');
    zbGmail = new Gmail();
    console.log('Hello ', zbGmail.get.user_email());
    document.body.setAttribute('zbSender', zbGmail.get.user_email());

    //channel
    //getOrCreateToken(openChannel);
    watchCompose(attachTrackCheckbox);
    //registerTab();
    zbGmail.observe.before('send_message', function(url, body, data, xhr) {
        console.log("OK?");
        var bps = xhr.xhrParams.body_params;
        console.log(bps);
        console.log(bps.zbTrack);
        if(bps.zbTrack === "1"){
            console.log('track this email');
            var result = addBeacon(bps);
            if(typeof result.error != undefined){
                bps.body = result.body;
                sendBeaconToServer(result.payload);
            }
        }
    });
};

function launch() {
    console.log('launch');
    if (typeof Gmail == 'undefined') {
        setTimeout(function() {
            console.log('setTimeout launch');
            launch();
        }, 5000);
    } else {
        refresh(main);
    }
}
if(typeof GLOBALS != 'undefined'){
    console.log(location.href);
    launch();
}

