var zbBaseURL = 'https://zenblip.appspot.com';

//https://github.com/flyakite/deps.js
var config = {
  paths: {
    'jsapi': zbBaseURL + '/_ah/channel/jsapi',
    'gapi': 'https://apis.google.com/js/client.js?onload=init',
    'jquery': chrome.extension.getURL('jquery-1.10.2.min.js'),
    'gmail': chrome.extension.getURL('gmail.js'),
    'utils': chrome.extension.getURL('utils.js'),
    'channel': chrome.extension.getURL('channel.js'),
    'messenger': chrome.extension.getURL('messenger.js'),
    'tracker': chrome.extension.getURL('tracker.js'),
    'databind': chrome.extension.getURL('vendors/databind/js/databind.js'),
    'simplemodal': chrome.extension.getURL('vendors/simplemodal/js/jquery.simplemodal.min.js'),
    'pickadate': chrome.extension.getURL('vendors/pickadate/js/picker.js'),
    'pickadate.date': chrome.extension.getURL('vendors/pickadate/js/picker.date.js'),
    'composeToolBox': chrome.extension.getURL('composeToolBox/js/composeToolBox.js'),
    'main': chrome.extension.getURL('main.js')
  },
  shim: {
    'channel': {
      'deps': ['utils']
    },
    'simplemodal': {
      'deps': ['jquery']
    },
    'pickadate': {
      'deps': ['jquery']
    },
    'pickadate.date': {
      'deps': ['jquery', 'pickadate']
    },
    'composeToolBox': {
      'deps': ['utils', 'jquery', 'databind', 'simplemodal', 'pickadate', 'pickadate.date']
    },
    'main':{
      // 'deps': ['jsapi', 'jquery', 'gmail', 'channel', 'messenger', 'tracker', 'simplemodal', 'databind']
      'deps': ['gapi', 'jsapi', 'jquery','gmail', 'channel', 'messenger', 'tracker', 'composeToolBox']
    }
  },
  css:{
    'font-awesome': chrome.extension.getURL('font-awesome/css/font-awesome.min.css'),
    'dashboard': chrome.extension.getURL('dashboard/css-build/tracker-dashboard.css'),
    'simplemodal': chrome.extension.getURL('vendors/simplemodal/css-build/simplemodal.css'),
    'pickadate': chrome.extension.getURL('vendors/pickadate/css/default.css'),
    'pickadate.date': chrome.extension.getURL('vendors/pickadate/css/default.date.css'),
    'composeToolBox': chrome.extension.getURL('composeToolBox/css-build/composeToolBox.css'),
    'content': chrome.extension.getURL('content.css')
  }
};
deps.config(config);
deps.load('main');

//TODO: remove this
document.addEventListener('zbNotificationMessage', function(e){
  console.log('zbNotificationMessage');
  console.log(e.detail);
  chrome.runtime.sendMessage(null, e.detail);
});

//add version details
chrome.runtime.sendMessage(null, {e:'zbGetExtDetails'}, null, function(response){
  if(response){
    console.log('zbGetExtDetails response');
    var t = document.createElement('script');
    t.text = " \
    var zbExtDetails = {version:'"+response.version+"'}; \
    ";
    (document.head || document.documentElement).appendChild(t);
  }
});

//zenblip module
var zenblip = (function(zb, $, React) {
  console.log(zb);

  var ExtensionID = 'oocgfjghhllncddlnhlocnikogonjdcp';
  var zbBaseURL = 'https://zenblip.appspot.com';
  var zbMainURL = 'https://www.zenblip.com';
  var zbExternalURL = 'http://www.email-link.com';
  var zbChannelPath = '/channels/';
  var signalResourcePath = '/resource/signals';
  var linkResourcePath = '/resource/links';
  var activityReportPath = '/activity_report';
  var authUserPath = '/auth/user';
  var current_user = null;
  var gmail = null;
  var sender = null;
  // var senderEmail;
  //var messenger;
  var raDashboard;
  var composeIDs = [];
  var debugCounter = 0;
  var zenblipAccessToken = '';
  var zbRedirectPath = '/l',
    zbSignalPath = '/s',
    zbTmpToken = '$$$zbTmpToken$$$';

  var setting = null;

  zb.FREE_PLAN = 0;
  zb.PRO_PLAN = 1;
  zb.TEAM_PLAN = 2;

  zb.Setting = function() {
    this.track_by_default = true;
    this.has_refresh_token = false;
    this.enable_reminder = false;
    this.plan = zb.FREE_PLAN;
  };

  // var contentMessageHandler = function(msg) {
  //   console.log('contentMessageHandler');
  //   console.log(msg);
  //   if(msg.data.senderEmail != senderEmail){
  //     console.log('Not my message');
  //     return;
  //   }
  //   switch(msg.e){
  //     // case 'GotUser':
  //     //   break;
  //     default:
  //       console.log('Messenger default Error');
  //       break;
  //   }
  // };

  // zb.trackerInit = function() {
  //   zb.Gmail.observe.before('send_message', zb.emailBeforeSend);
  //   zb.watchCompose(zb.attachTrackCheckbox);
  //   zb._trackerInitialized = true;
  // };

  // zb.ChannelInit = function() {
  //   var options = {
  //     isCreate: false, 
  //     senderEmail:sender.email,
  //     uri: zbBaseURL + zbChannelPath
  //   };
  //   //def in channel.js
  //   zb.getOrCreateChannelToken(options, function() {
  //     zb.openChannel(options);
  //   });
  // };
  
  // zb.SenderInit = function() {
  //   messenger.post({'e':'SenderInit','sender':sender.email,'ukey':sender.ukey})
  // };
  zb.DashboardInit = function() {
    var dashboard = document.createElement('div');
    dashboard.id = 'zenblip-dashboard-container';
    $('div.nH.w-asV.aiw')[0].appendChild(dashboard);
    // zb.getElementByXpath("/html/body/div[7]/div[3]/div/div[1]").appendChild(dashboard);
    var dashboardHeight = '300px';
    raDashboard = React.render(
      React.createElement(SignalApp, {
        senderEmail: sender.email, 
        baseURL: zbBaseURL, 
        signalResourcePath: signalResourcePath,
        linkResourcePath: linkResourcePath,
        activityReportPath: activityReportPath,
        dashboardHeight: dashboardHeight
      }),
      document.getElementById(dashboard.id)
    );
    //mixpanel
    // $('body').on('click', '.track', function(){
    //   var $this = $(this);
    //   console.log($this.data('track'));
    //   mixpanel.track($this.data('track'), $this.data('trackop'));
    // });
  };

  zb.getAndUpdateUserInfo = function(interactive) {
    //This function is used in dashboard.js
    // console.log('zb.getAndUpdateUserInfo');
    // var options = {interactive:interactive}
    // messenger.post({e:'getAndUpdateUserInfo', options:options});

    zb.loginZenblip(sender.email);
    // zb.goToGoogleOAuth(senderEmail);
  };

  // zb.validateUserPlan = function(senderEmail) {
  //   console.log('zb.validateUserPlan');
  //   var options = {'check_permission_email': senderEmail};
  //   messenger.post({e:'validateUserPlan', options:options})
  // };
  zb.loginZenblip = function(hintEmail) {
    window.location.href = zbMainURL + "/accounts/login/?next=" +
      encodeURIComponent('/accounts/redirect?u='+encodeURIComponent(window.location.href));
  };

  zb.goToGoogleOAuth = function(hintEmail) {
    var url = "https://accounts.google.com/o/oauth2/auth?" + 
      "response_type=code" +
      "&client_id=" + encodeURIComponent("709499323932-c4a99dsihk6v1js29vg9tg3n30ph0oq8.apps.googleusercontent.com") +
      "&redirect_uri=" + encodeURIComponent(zbBaseURL + "/auth/oauth2callback") +
      "&scope=" + encodeURIComponent("email profile https://mail.google.com/") +
      "&state=" + encodeURIComponent(window.location.href) +
      "&access_type=offline" +
      "&approval_prompt=force" +
      "&login_hint=" + encodeURIComponent(hintEmail) +
      "&include_granted_scopes=true";
    
    window.location.href = url;
  };
  zb.UserInit = function() {
    //zb.getDirectAccessToken();
    //TODO: get local stored permission before asking remote server
    zb.getJSONPAccessTokenAndCheckPermission(sender.email);
    //zb.getAndUpdateUserInfo(false);
    // zb.validateUserPlan();
  };

  zb.redirectToAccountManagement = function(hintEmail) {
    window.location.href = zbMainURL + "/dashboard?" +
      "hint=addplan" +
      "&email=" + hintEmail +
      "&state=" + encodeURIComponent(window.location.href);
  };

  // JSONP way
  zb.getJSONPAccessTokenAndCheckPermission = function(email) {
    //HTTPS is required
    // var script = document.createElement('script');
    // script.src = zbMainURL + '/accounts/access_token?callback=zenblip.gotJSONPAccessToken&check_permission_email=' + checkEmail;
    // //script.src = 'https://127.0.0.1:8000/accounts/access_token?callback=zenblip.gotJSONPAccessToken&email=' + senderEmail;
    // document.body.appendChild(script);
    var url = zbMainURL + '/accounts/access_token';
    $.getJSON(url, {check_permission_email:email}, zb.gotJSONPAccessToken);
  };

  //JSONP callback
  zb.gotJSONPAccessToken = function(data) {

    var error, hasPermission, signedIn;
    console.log('gotJSONPAccessToken');
    console.log(data);
    if(data.signed_in){
      zenblipAccessToken = data.access_token;
      if(data.has_permission){
        setting.plan = data.top_plan_order;
        if(setting.plan == zb.FREE_PLAN){
          //free plan
          raDashboard.onAuthenticationFailed({message:'zenblip free plan enabled', collapse:true});
        }else if([zb.PRO_PLAN, zb.TEAM_PLAN].indexOf(setting.plan) != -1){
          //paid plan
          raDashboard.onAuthenticated({senderEmail:sender.email, accessToken:zenblipAccessToken});
        }
        if(!zb._trackerInitialized){
          zb.requestTrackerInit({zenblipAccessToken:zenblipAccessToken});
        }
      }else{
        raDashboard.onAuthenticationFailed({message:'Add ' + senderEmail + ' to zenblip'});
        //to be removed -----
        // zenblipAccessToken = '1lk3j5hgl1k5g15ATHATH35523jkgETHWYqetrkj_THTHQ25hwTYH2556DHMETJM2452h25'
        // raDashboard.onAuthenticated({senderEmail:sender.email, accessToken:zenblipAccessToken});
        // if(!zb._trackerInitialized){
        //  zb.requestTrackerInit({zenblipAccessToken:zenblipAccessToken});
        //  setting.plan = zb.TEAM_PLAN;
        // }
        //to be removed -----
      }
    }else{
      raDashboard.onAuthenticationFailed({});
      //to be removed -----
      // zenblipAccessToken = '1lk3j5hgl1k5g15ATHATH35523jkgETHWYqetrkj_THTHQ25hwTYH2556DHMETJM2452h25'
      // raDashboard.onAuthenticated({senderEmail:sender.email, accessToken:zenblipAccessToken});
      // if(!zb._trackerInitialized){
      //   zb.requestTrackerInit({zenblipAccessToken:zenblipAccessToken});
      //   setting.plan = zb.TEAM_PLAN;
      // }
      //to be removed -----
    }
  };

  zb.requestTrackerInit = function(options) {
    $.get(zbBaseURL+'/settings', {email:sender.email, access_token:options.zenblipAccessToken, ref:'gmail-chrome'}, function(data) {
      console.log(data);
      if(data.error != 1){
        setting.track_by_default = data.track_by_default;
        setting.has_refresh_token = data.has_refresh_token;
      }else{
        setting.track_by_default = true;
        setting.has_refresh_token = false;
      }
      if([zb.PRO_PLAN, zb.TEAM_PLAN].indexOf(setting.plan) != -1 && !setting.has_refresh_token){
        zb.goToGoogleOAuth(sender.email);
      }else{
        setting.enable_reminder = true;
      }

      //zb tracker init in main.js
      window.postMessage({type:'zbTrackerInit', zenblipAccessToken:options.zenblipAccessToken, setting:setting}, "https://mail.google.com");
      zb._trackerInitialized = true;
    });
  };

  zb.Init = function(options){
    console.log('zenblip init');
    sender = options.sender;
    //senderEmail = options.senderEmail;
    //messenger = new zb.Messenger(ExtensionID, contentMessageHandler, sender);
    zb.DashboardInit();
    zb.UserInit(); // get access token and launch dashboard
    //zb.SenderInit();
    setting = new zb.Setting();
  };
  return zb;
}(zenblip || {}, jQuery, React));

document.addEventListener('zbInit', function(e){
  console.log('zbInit');
  //console.log(e.detail);
  zenblip.Init(e.detail);
});
