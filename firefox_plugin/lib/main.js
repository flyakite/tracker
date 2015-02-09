// var buttons = require('sdk/ui/button/action');
// var tabs = require("sdk/tabs");

// var button = buttons.ActionButton({
//   id: "mozilla-link",
//   label: "Visit Mozilla",
//   icon: {
//     "16": "./icon-16.png",
//     "32": "./icon-32.png",
//     "64": "./icon-64.png"
//   },
//   onClick: handleClick
// });

// function handleClick(state) {
//   tabs.open("http://www.mozilla.org/");
// }

var pageMod = require('sdk/page-mod');
var self = require('sdk/self');

pageMod.PageMod({
  include:["https://mail.google.com/*"],
  contentScriptFile: [
    self.data.url('content.js')
    ],
  contentScript: "\
  var resourcePath = {'jquery-1.10.2.min.js':'"+self.data.url('jquery-1.10.2.min.js')+"',\
                      'gmail.js':'"+self.data.url('gmail.js')+"',\
                      'contentMain.js':'"+self.data.url('contentMain.js')+"',\
                      };\
  loadContentScripts(resourcePath);\
  ",
  contentScriptWhen: 'end'
});