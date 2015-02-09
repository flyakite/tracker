var zbBaseURL = 'https://zenblip.appspot.com';

//https://github.com/flyakite/deps.js
var config = {
  paths: {
    'jsapi': zbBaseURL + '/_ah/channel/jsapi',
    'jquery': chrome.extension.getURL('jquery-1.10.2.min.js'),
    'gmail': chrome.extension.getURL('gmail.js'),
    'react': chrome.extension.getURL('react-with-addons.min.js'),
    'export': chrome.extension.getURL('dashboard/utils/excellentexport.min.js'),
    'mixpanel': chrome.extension.getURL('dashboard/utils/mixpanel.js'),
    'dashboard': chrome.extension.getURL('dashboard/js-build/dashboard.js'),
    'utils': chrome.extension.getURL('utils.js'),
    'channel': chrome.extension.getURL('channel.js'),
    'main': chrome.extension.getURL('main.js')
  },
  shim: {
    'jsapi':{
      'waitSeconds': 5,
      'retry': 3
    },
    'dashboard':{
      'deps': ['react', 'jquery', 'export', 'mixpanel']
    },
    'channel': {
      'deps': ['utils']
    },
    'main':{
      'deps': ['jsapi', 'jquery', 'gmail', 'dashboard', 'utils', 'channel']
    }
  },
  css:{
    'font-awesome': chrome.extension.getURL('font-awesome/css/font-awesome.min.css'),
    'dashboard': chrome.extension.getURL('dashboard/css-build/dashboard.css'),
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

//TODO: remove this
// document.addEventListener('zbSenderInit', function(e){
//   console.log('zbSenderInit');
//   console.log(e.detail);
//   chrome.runtime.sendMessage(null, e.detail);
// });

//TODO: remove this
// document.addEventListener('zbGetUserInfoOrShowAuthentication', function(e){
//   console.log('zbGetUserInfoOrShowAuthentication');
//   console.log(e.detail);
//   chrome.runtime.sendMessage(null, e.detail, null, function(response){
//     console.log('zbGetUserInfoOrShowAuthentication response');
//     console.log(response.email);
//     $('#zbName').text(response.email);
//   });
// });

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
