
var zenblip = (function(zb) {

  zb.uuid = function(){
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
      return v.toString(16);
    });
  };
  zb.hashCode = function(string) {
    var hash = 0;
    if (string.length === 0) return hash.toString();
    for (i = 0; i < string.length; i++) {
      char = string.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return hash.toString();
  };

  zb.hashFnv32a = function (str, asString, seed) {
    /*jshint bitwise:false */
    var i, l,
      hval = (seed === undefined) ? 0x823c6b3a : seed;

    for (i = 0, l = str.length; i < l; i++) {
      hval ^= str.charCodeAt(i);
      hval += (hval << 1) + (hval << 4) + (hval << 7) + (hval << 8) + (hval << 24);
    }
    if( asString ){
      // Convert to 8 digit hex string
      return ("0000000" + (hval >>> 0).toString(16)).substr(-8);
    }
    return hval >>> 0;
  };

  zb.getElementByXpath = function(path) {
    return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
  };

  /**** retryConnection *****/
  var retryConnectionRegistry = {};
  zb.retryConnection = {
    hold: function(registerID, timeout, callback) {
      // console.log('hold' + registerID + ' ' + timeout);
      var control = setTimeout(function() {
        retryConnectionRegistry[registerID] = {};
        callback();
      }, timeout);
      retryConnectionRegistry[registerID] = { 'timeout': timeout,
                          'control': control};
    },
    release: function(registerID) {
      // console.log('release ' + registerID);
      if (retryConnectionRegistry[registerID]){
        // console.log('release control');
        // console.log(retryConnectionRegistry[registerID]);
        clearTimeout(retryConnectionRegistry[registerID].control);
      }
      retryConnectionRegistry[registerID] = {};  
    },
  };

  /*** cookie ***/
  zb.setCookie = function(name,value,seconds) {
    if (seconds) {
      var date = new Date();
      date.setTime(date.getTime()+(seconds*1000));
      var expires = "; expires="+date.toGMTString();
    }
    else var expires = "";
    document.cookie = name+"="+value+expires+"; path=/";
  };

  zb.getCookie = function(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
      var c = ca[i];
      while (c.charAt(0)==' ') c = c.substring(1,c.length);
      if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
  };

  zb.deleteCookie = function(name) {
    zb.setCookie(name,"",-1);
  };
  
  return zb;
}(zenblip || {}));