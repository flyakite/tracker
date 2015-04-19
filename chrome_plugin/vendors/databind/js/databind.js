//https://github.com/grnadav/databind
"use strict";!function(e){"function"==typeof define&&define.amd?define(e):window.DataBind=e()}(function(){function e(e){return e&&window.jQuery&&e instanceof window.jQuery}function t(t){return e(t)?t[0]:t}function n(e,t){if(!e)return void 0;var n=void 0!==t;if(["checkbox","radio"].indexOf(e.type)>=0)return n&&(e.checked=!!t),e.checked;if(["text","textarea","select-one","email","url","week","time","search","tel","range","number","month","datetime-local","date","color","password"].indexOf(e.type)>=0)return n&&(e.value=t),e.value;if(["select-multiple"].indexOf(e.type)>=0){n&&(r(t)||(t=[t]));for(var o,i=[],a=e&&e.options,c=0,u=a.length;u>c;c++)o=a[c],n&&(o.selected=t.indexOf(o.value)>-1?!0:!1),o.selected&&i.push(o.value||o.text);return i}return n&&(e.innerText=t),e.innerText}function r(e){return"[object Array]"===Object.prototype.toString.call(e)}function o(e){return["checkbox","radio","select-one","select-multiple","password"].indexOf(e.type)>=0?"change":["text","textarea","email","url","week","time","search","tel","range","number","month","datetime-local","date","color"].indexOf(e.type)>=0?"input":void 0}function i(e){return e.hashkey||(e.hashkey=Date.now()+Math.floor(1e5*Math.random())),e.hashkey}function a(e,t){if(e&&t){var n=i(e);if(M[n]=M[n]||[],!(M[n].indexOf(t)>-1)){M[n].push(t);var r=o(e);e.addEventListener(r,t,!1)}}}function c(e,t){var n=i(e),r=M[n].indexOf(t);if(M[n]&&-1!==r){M[n].splice(r,1);var a=o(e);e.removeEventListener(a,t,!1)}}function u(e){var t=i(e),n=M[t];if(e&&n){var r,o=n.concat(),a=o.length;for(r=0;a>r;r++)c(e,o[r])}}function f(e,t){function n(){var e,t,n=!1;return t=o.exec(i[r]),t&&t.length&&(e=i[r].split("[")[0],a=a[e][+t[1]],n=!0),n}var r,o=new RegExp(/.*\[(\d+)\]/),i=t.split("."),a=e;for(r=0;r<i.length-1;r++)n()||(a=a[i[r]]);return n(),a}function l(e,t,n){var r=t.split("."),o=f(e,t);return void 0!==n&&(o[r[r.length-1]]=n),o[r[r.length-1]]}function s(e,t,r){var o=function(e,t,n,r,o,i,a,c){return function(){var e=o(this),u=i(this),f=r(t,n);r(t,n,e),a(c,this,{key:u,oldValue:f,newValue:e})}}(e,t,r,l,n,v,j,_);a(e,o)}function d(e){u(e)}function h(e,t,r){var o=function(e,t,n,r,o,i,a){return function(t,n,c,u){var t=i(e);r(e,c),o(a,e,{key:t,oldValue:u,newValue:c})}}(e,t,r,n,j,v,S);E.watch(t,r,o)}function p(e,t){var n,r=e.watchers[t];for(n=0;n<r.length;n++)E.unwatch(e,t,r[n])}function v(e){return e?e.getAttribute(L):void 0}function m(e){return e=e||{},e={dom:void 0!==e.dom?e.dom:!0,model:void 0!==e.model?e.model:!0,children:void 0!==e.children?e.children:!0}}function g(e,t){if(!e||!t)return{};var n=v(e);if(!n)return{};var r=f(t,n),o=n.split(".");return o=o[o.length-1],{key:n,deepKey:o,deepModel:r,keyExists:!!r}}function y(e,t,r){if(!e||!t)return!1;var o=g(e,t);if(!o.keyExists)return!1;var i=l(t,o.key);return n(e,i),r.dom&&s(e,o.deepModel,o.deepKey),r.model&&h(e,o.deepModel,o.deepKey),!0}function w(e,t,n){if(e&&t){var r=g(e,t);r.keyExists&&(n.dom&&d(e),n.model&&p(r.deepModel,r.deepKey))}}function b(e,t){var n,r,o=[e];if(t.children)for(n=e.getElementsByTagName("*"),r=0;r<n.length;r++)o.push(n[r]);return o}function j(e,t,n){var r=document.createEvent("Events");r.initEvent(e,!0,!0),r.data=n,t.dispatchEvent(r)}function x(e,t,n,r){function o(e,o){f.push(o),r.dom&&e.addEventListener(n,o,!1),r.model&&e.addEventListener(t,o,!1)}function i(e,t){var n=f.indexOf(t);-1!==n&&(f.splice(n,1),r.dom&&e.removeEventListener(_,t,!1),r.model&&e.removeEventListener(S,t,!1))}function a(e){var t,n=f.concat();for(t=0;t<n.length;t++)i(e,n[t])}function c(t){var n;for(n=0;n<e.length;n++)o(e[n],t)}function u(t){var n,r=i;for(void 0===t&&(r=a),n=0;n<e.length;n++)r(e[n],t)}var f=[];return{watch:c,unwatch:u}}function O(e,n,r){if(e&&n){var o=t(e);if(o!==e)return arguments[0]=o,O.apply(this,arguments);r=m(r);var i,a,c=b(e,r),u=[];for(i=0;i<c.length;i++)a=y(c[i],n,{dom:r.dom,model:r.model}),a&&u.push(c[i]);var f=new x(u,S,_,r);return e.watchable=f,f}}function k(e,n,r){if(e&&n){var o=t(e);if(o!==e)return arguments[0]=o,k.apply(this,arguments);r=m(r);var i,a=b(e,r);for(i=0;i<a.length;i++)w(a[i],n,{dom:r.dom,model:r.model});e.watchable.unwatch()}}var E=function(){var e={noMore:!1},t=[],n=function(e){var t={};return e&&"[object Function]"==t.toString.call(e)},r=function(e){return e%1===0},o=function(e){return"[object Array]"===Object.prototype.toString.call(e)},i=function(e,t){var n=[],r=[];if("string"!=typeof e&&"string"!=typeof t&&!o(e)&&!o(t)){for(var i in e)t[i]||n.push(i);for(var a in t)e[a]||r.push(a)}return{added:n,removed:r}},a=function(e){if(null==e||"object"!=typeof e)return e;var t=e.constructor();for(var n in e)t[n]=e[n];return t},c=function(e,t,n,r){try{Object.defineProperty(e,t,{get:n,set:r,enumerable:!0,configurable:!0})}catch(o){try{Object.prototype.__defineGetter__.call(e,t,n),Object.prototype.__defineSetter__.call(e,t,r)}catch(i){throw"watchJS error: browser not supported :/"}}},u=function(e,t,n){try{Object.defineProperty(e,t,{enumerable:!1,configurable:!0,writable:!1,value:n})}catch(r){e[t]=n}},f=function(){n(arguments[1])?l.apply(this,arguments):o(arguments[1])?s.apply(this,arguments):d.apply(this,arguments)},l=function(e,t,n,r){if("string"!=typeof e&&(e instanceof Object||o(e))){var i=[];if(o(e))for(var a=0;a<e.length;a++)i.push(a);else for(var c in e)i.push(c);s(e,i,t,n,r)}},s=function(e,t,n,r,i){if("string"!=typeof e&&(e instanceof Object||o(e)))for(var a in t)d(e,t[a],n,r,i)},d=function(e,t,r,i,a){"string"!=typeof e&&(e instanceof Object||o(e))&&(n(e[t])||(null!=e[t]&&(void 0===i||i>0)&&(void 0!==i&&i--,l(e[t],r,i)),m(e,t,r),a&&O(e,t,r,i)))},h=function(){n(arguments[1])?p.apply(this,arguments):o(arguments[1])?v.apply(this,arguments):j.apply(this,arguments)},p=function(e,t){if(!(e instanceof String)&&(e instanceof Object||o(e))){var n=[];if(o(e))for(var r=0;r<e.length;r++)n.push(r);else for(var i in e)n.push(i);v(e,n,t)}},v=function(e,t,n){for(var r in t)j(e,t[r],n)},m=function(t,n,r){var o=t[n];b(t,n),t.watchers||u(t,"watchers",{}),t.watchers[n]||(t.watchers[n]=[]);for(var i in t.watchers[n])if(t.watchers[n][i]===r)return;t.watchers[n].push(r);var a=function(){return o},f=function(i){var a=o;o=i,t[n]&&l(t[n],r),b(t,n),e.noMore||JSON.stringify(a)!==JSON.stringify(i)&&(g(t,n,"set",i,a),e.noMore=!1)};c(t,n,a,f)},g=function(e,t,n,o,i){for(var a in e.watchers[t])r(a)&&e.watchers[t][a].call(e,t,n,o,i)},y=["pop","push","reverse","shift","sort","slice","unshift"],w=function(e,t,n,r){u(e[t],r,function(){var o=n.apply(e[t],arguments);return d(e,e[t]),"slice"!==r&&g(e,t,r,arguments),o})},b=function(e,t){if(e[t]&&!(e[t]instanceof String)&&o(e[t]))for(var n,r=y.length;r--;)n=y[r],w(e,t,e[t][n],n)},j=function(e,t,n){for(var r in e.watchers[t]){var o=e.watchers[t][r];o==n&&e.watchers[t].splice(r,1)}k(e,t,n)},x=function(){for(var e in t){var n=t[e],r=i(n.obj[n.prop],n.actual);if(r.added.length||r.removed.length){if(r.added.length)for(var o in n.obj.watchers[n.prop])s(n.obj[n.prop],r.added,n.obj.watchers[n.prop][o],n.level-1,!0);g(n.obj,n.prop,"differentattr",r,n.actual)}n.actual=a(n.obj[n.prop])}},O=function(e,n,r,o){t.push({obj:e,prop:n,actual:a(e[n]),watcher:r,level:o})},k=function(e,n,r){for(var o in t){var i=t[o];i.obj==e&&i.prop==n&&i.watcher==r&&t.splice(o,1)}};return setInterval(x,50),e.watch=f,e.unwatch=h,e.callWatchers=g,e}(),M={},S="databind-model-change",_="databind-dom-change",L="data-key";return{bind:O,unbind:k}});