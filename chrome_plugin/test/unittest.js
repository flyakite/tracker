
var zbBaseURL = 'https://zenblip.appspot.com';
var zbExternalURL = 'http://www.email-link.com';
var zbRedirectPath = '/l';

module('Test Replace Links');
test('replace links', function() {
  var emailBody = " \
  Hello \
  http://www.google.com \
  <a href='http://www.google.com'>http://www.google.com</a> \
  <a href='http://www.google.com'>Google</a> \
  <a href='http://www.email-link.com/l/-1234/abc/def'>Google</a> \
  Tom \
  ";
  console.log(zenblip);
  var links = zenblip.parseLink(emailBody, zbExternalURL);
  equal(links.length, 3, 'email body has 3 links');

  var l = links[0];
  equal(l.plain, 0, 'plain');
  equal(l.url, 'http://www.google.com', 'url');
  equal(l.urlDecoded, 'http://www.google.com', 'urlDecode');
  equal(l.urlHash, '1244095381', 'urlHash');
  equal(l.urlText, 'http://www.google.com', 'urlText');
  equal(l.urlWithAtag, "<a href='http://www.google.com'>http://www.google.com</a>", 'urlWithAtag');


  l = links[1];
  equal(l.plain, 0, 'plain');
  equal(l.url, 'http://www.google.com', 'url');
  equal(l.urlDecoded, 'http://www.google.com', 'urlDecode');
  equal(l.urlHash, '1244095381', 'urlHash');
  equal(l.urlText, 'Google', 'urlText');
  equal(l.urlWithAtag, "<a href='http://www.google.com'>Google</a>", 'urlWithAtag');

  l = links[2];
  equal(l.plain, 1);
  equal(l.url,'http://www.google.com');
  equal(l.urlDecoded, 'http://www.google.com');
  equal(l.urlHash, '1244095381');
  equal(l.urlText, null);
  equal(l.urlWithAtag, null, 'urlWithAtag');

  var token = zenblip.uuid().replace(/-/g,'').substr(-20);
  var ukey = '-123491876';
  var bodyLinksReplaced = zenblip.replaceLinks(emailBody, token, links, ukey, zbExternalURL, zbRedirectPath);
  console.log(bodyLinksReplaced);
  var replacedUrl = zbExternalURL + zbRedirectPath + '/' + ukey + '/' + token;
  var re = new RegExp(replacedUrl, 'g');
  var zbExternalURLOccursNTimes = bodyLinksReplaced.match(re).length;
  equal(zbExternalURLOccursNTimes, 3);
  var re2 = new RegExp('http://www.google.com', 'g');
  var originalURLOccursNTimes = bodyLinksReplaced.match(re2);
  equal(originalURLOccursNTimes, null);
  var re3 = new RegExp('www.google.com', 'g');
  var castratedURLOccursNTimes = bodyLinksReplaced.match(re3).length;
  equal(castratedURLOccursNTimes, 5);
});