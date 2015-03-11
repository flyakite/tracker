var zenblip = (function(zb) {
  zb.purgeBody = function(body) {
    return body.replace('<wbr>', ''); //TODO: WTF?
  };
  zb.parseLink = function(body, zbExternalURL) {
    var urlPack = function(url, isPlain, urlText, urlWithAtag) {
      var urlDecoded,
        urlHash,
        urlText,
        urlWithAtag;
      //urlDecoded = url.replace(/&amp;/g, '&'); //TODO:improve this if necessary //remove this to fix Gmail Error
      urlDecoded = url;
      urlHash = zb.hashCode(urlDecoded);
      return {
        url: url,
        urlDecoded: urlDecoded,
        urlHash: urlHash,
        plain: isPlain,
        urlText: urlText,
        urlWithAtag: urlWithAtag
      };
    };
    console.log('parseLink');
    try {
      var linkRegexWithATag = /<[Aa][^<>]* [Hh][Rr][Ee][Ff]=[\"\']([Hh][Tt][Tt][Pp][Ss]?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:;%_\+.~#?&//=]*))[\"\'].*?>(.*?)<\/[Aa]>/g; //"
      var linkRegexInPlainText = /[Hh][Tt][Tt][Pp][Ss]?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:;%_\+.~#?&//=]*)/g,
        bodyDecoded = zb.purgeBody(body),
        links = [],
        plainLinks = [],
        linksDecoded = [],
        plainLinksDecoded = [];
      //deal with links with html A tag
      var match = linkRegexWithATag.exec(bodyDecoded);
      var url;
      var urlCount = 1;
      var _MAX_URL_COUNT = 200;
      while (match != null && urlCount < _MAX_URL_COUNT) {
        //console.log('urlmatch');
        urlWithAtag = match[0];
        url = match[1];
        urlText = match[4];
        if(url.indexOf(zbExternalURL) == -1){
          links.push(urlPack(url, 0, urlText, urlWithAtag));
        }
        match = linkRegexWithATag.exec(bodyDecoded);
        urlCount ++;
      }

      //deal with plain url link
      var bodyDecoded2 = bodyDecoded.replace(linkRegexWithATag, '');

      plainLinks = bodyDecoded2.match(linkRegexInPlainText);
      if (plainLinks != null && plainLinks.length > 0) {
        for (var i = plainLinks.length; i--;) {
          console.log('parselink ' + i);
          url = plainLinks[i];
          //do not record link already been replaced
          if(url.indexOf(zbExternalURL) == -1){
            links.push(urlPack(url, 1, null, null));
          }
        }
      }

      console.log(links);
      // bodyDecoded = bodyDecoded.replace(url, zbBaseURL + zbRedirectPath + '?t=' + zbTmpToken +'&h=' +urlHash);
      return links;
    } catch (e) {
      console.log(e);
      return [];
    }
  };

  zb.replaceLinks = function(body, token, links, ukey, zbExternalURL, zbRedirectPath) {
    var bodyDecoded = zb.purgeBody(body),
      tag, l, newURL, urlWithAtagUrlReplaced, urlTextCastrated;

    console.log('replaceLinks');
    for (var i = 0; i < links.length; i++) { //order sequence matters
      console.log('replaceLinks ' + i);
      l = links[i];
      newURL = zbExternalURL + zbRedirectPath + "/" + ukey + "/" + token + "/" + l.urlHash + "?url=" + encodeURIComponent(l.url);
      if (l.plain === 1) {
        //if plain, convert to html tag
        newURL = "<a href='" + newURL + "'>" + l.urlDecoded.replace(/^https?:\/\//i,'') + "</a>"; //remove starting http://
        bodyDecoded = bodyDecoded.replace(l.url, newURL);
      }else{
        if(typeof l.urlText != 'undefined' && typeof l.urlWithAtag != 'undefined'){
          urlTextCastrated = l.urlText.replace(/^https?:\/\//i,'');
          console.log(urlTextCastrated);
          urlWithAtagUrlReplaced = l.urlWithAtag.replace(l.url, newURL).replace(l.urlText, urlTextCastrated);
          console.log(urlWithAtagUrlReplaced);
          bodyDecoded = bodyDecoded.replace(l.urlWithAtag, urlWithAtagUrlReplaced);
        }
      }
    }
    return bodyDecoded;
  };
return zb;
}(zenblip || {}));