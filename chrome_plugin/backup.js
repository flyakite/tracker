//backgroundMain.js


// callback = function (error, httpStatus, responseText);
// function authenticatedXhr(method, url, callback) {
//   var retry = true;
//   function getTokenAndXhr() {
//     chrome.identity.getAuthToken({/* details */},
//                                  function (access_token) {
//       if (chrome.runtime.lastError) {
//         callback(chrome.runtime.lastError);
//         return;
//       }

//       var xhr = new XMLHttpRequest();
//       xhr.open(method, url);
//       xhr.setRequestHeader('Authorization',
//                            'Bearer ' + access_token);

//       xhr.onload = function () {
//         if (this.status === 401 && retry) {
//           // This status may indicate that the cached
//           // access token was invalid. Retry once with
//           // a fresh token.
//           retry = false;
//           chrome.identity.removeCachedAuthToken(
//               { 'token': access_token },
//               getTokenAndXhr);
//           return;
//         }

//         callback(null, this.status, this.responseText);
//       }
//     });
//   }
// }

function xhrWithAuth(method, url, interactive, callback) {
  var access_token;

  var retry = true;

  getToken();

  function getToken() {
    console.log('getToken');
    chrome.identity.getAuthToken({ interactive: interactive }, function(token) {
      if (chrome.runtime.lastError) {
        callback(chrome.runtime.lastError);
        return;
      }

      access_token = token;
      console.log('Got AuthToken');
      console.log(access_token);
      onGotAuthToken();
      // requestStart();
    });
  }

  function onGotAuthToken () {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', zbBaseURL + '/auth/chrome');
    xhr.setRequestHeader('Authorization', 'Bearer ' + access_token);
    xhr.onload = onPassAccessTokenComplete;
    xhr.send();
  }

  function onPassAccessTokenComplete () {
    console.log(this.status);
    console.log(this.response);
    console.log(this.response.email);
  }

  // function requestStart() {
  //   var xhr = new XMLHttpRequest();
  //   xhr.open(method, url);
  //   xhr.setRequestHeader('Authorization', 'Bearer ' + access_token);
  //   xhr.onload = requestComplete;
  //   xhr.send();
  // }

  // function requestComplete() {
  //   if (this.status == 401 && retry) {
  //     retry = false;
  //     chrome.identity.removeCachedAuthToken({ token: access_token },
  //                                           getToken);
  //   } else {
  //     callback(null, this.status, this.response);
  //   }
  // }
}

function getUserInfo(interactive) {
  xhrWithAuth('GET',
              'https://www.googleapis.com/userinfo/v2/me',
              interactive,
              onUserInfoFetched);
}

function onUserInfoFetched (error, status, response) {
  if (!error && status == 200) {
    var user_info = JSON.parse(response);
    console.log(user_info);

  } else {
    console.log({status:status,error:status});
  }
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
// var main = function() {
  // getUserInfo(true);
  // Messagelistener();

    // getToken(openChannel);

    // function show() {
        // var time = /(..)(:..)/.exec(new Date()); // The prettyprinted time.
        // var hour = time[1] % 12 || 12; // The prettyprinted hour.
        // var period = time[1] < 12 ? 'a.m.' : 'p.m.'; // The period of the day.
        // new Notification(hour + time[2] + ' ' + period, {
            // icon: '48.png',
            // body: 'Time to make the toast.'
        // });
    // }
    // show();


    // $.get(zbBaseURL + '/auth/check', {
        // "from": "background"
    // }, function(jdata) {
        // console.log(jdata);
        // if (jdata.login_url) {
            // window.open(zbBaseURL + jdata.login_url);
        // }
    // });
// };

function main () {
  // disable for now, too much process for the client
  // getUserInfo(true);
}