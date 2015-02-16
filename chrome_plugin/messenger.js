/* messenger */
var zenblip = (function(zb) {
  zb.Messenger = function(extensionID, messageHandler, sender){
    this.extensionID = extensionID;
    this.sender = sender;
    this.port = chrome.runtime.connect(extensionID);
    this.port.onMessage.addListener(messageHandler);
    this.port.onDisconnect.addListener(function() {
      console.log('Messenger Disconnected');
    });
  };

  zb.Messenger.prototype.post = function(data){
    // if(typeof senderEmail != 'undefined'){
    //   data.senderEmail = senderEmail;
    // }
    this.port.postMessage(data);
  };

  return zb;
}(zenblip || {}));
/*** end of messenger */