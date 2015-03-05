var ListDetail = React.createClass({displayName: "ListDetail",
  locationToString: function() {
    var location = "";
    if( this.props.data.city != null && this.props.data.country != null ){
      location = ""+this.props.data.city + " ," + this.props.data.country;
    }
    if( this.props.data.country != null ){
      location = ""+this.props.data.country;
    }
    return location;
  },
  dateObjectToString: function(date) {
    var d0 = new Date();
    d = new Date((date.timestamp)*1000);
    var month = d.getMonth() + 1;
    return "" + d.getFullYear() + "/" + ("0" + month).slice(-2) +"/"+ ("0"+d.getDate()).slice(-2) +" "+ 
      ("0" + d.getHours()).slice(-2) +":"+ ("0" + d.getMinutes()).slice(-2);
  },
  render: function() {
    switch(this.props.contentType){
      case 'EmailTracked':
        var detail = 'Sent: ' + this.dateObjectToString(this.props.data.created);
        return (
          React.createElement("div", null, 
            React.createElement("span", null, detail)
          )
        );
        break;
      case 'EmailOpened':
        var opened = 'Opened: ' + this.dateObjectToString(this.props.data.modified);
        var locationInfo = this.locationToString() == "" ? "": "Location: " + this.locationToString();
        var deviceInfo = this.props.data.device == null ? "": "Device: " + this.props.data.device;
        var accessCountInfo = this.props.data.access_count == null ? "": "Frequency: " + this.props.data.access_count;
        return (
          React.createElement("div", null, 
            React.createElement("span", null, opened), 
            React.createElement("span", null, locationInfo), 
            React.createElement("span", null, deviceInfo), 
            React.createElement("span", null, accessCountInfo)
          )
        );
        break;
      case 'EmailNotOpened':
        var detail = 'Sent: ' + this.dateObjectToString(this.props.data.created);
        return (
          React.createElement("div", null, 
            React.createElement("span", null, detail)
          )
        );
        break;
      case 'LinkClicked':
        var clicked = ' Clicked: ' + this.dateObjectToString(this.props.data.modified);
        var locationInfo = this.locationToString() == "" ? "": "Location: " + this.locationToString();
        var deviceInfo = this.props.data.device == null ? "": "Device: " + this.props.data.device;
        var accessCountInfo = this.props.data.access_count == null ? "": "Frequency: " + this.props.data.access_count;
        return (
          React.createElement("div", null, 
            React.createElement("span", {className: "zb-link-url"}, 
              React.createElement("a", {target: "_blank", href: this.props.data.url}, this.props.data.url.substr(0,50)+'...')
            ), 
            React.createElement("span", null, clicked), 
            React.createElement("span", null, locationInfo), 
            React.createElement("span", null, deviceInfo), 
            React.createElement("span", null, accessCountInfo)
          )
        );
        break;
      default:
        break;
    }
  }
})


var ListNode = React.createClass({displayName: "ListNode",
  render: function() {
    //console.log(this.props.contentType);
    //console.log(this.props.data);
    var receiver;
    if( this.props.data.receiver_emails && this.props.data.receiver_emails !=0 ){
      receiver = this.props.data.receiver_emails[0];
    }else if( this.props.data.receivers && this.props.data.receivers.to){
      receiver = Object.keys(this.props.data.receivers.to)[0]
    }
    var detail, locationInfo, deviceInfo;
    return (
      React.createElement("tr", {className: "zb-list-row"}, 
        React.createElement("td", {className: "zb-receiver"}, 
          React.createElement("span", null, receiver)
        ), 
        React.createElement("td", {className: "zb-subject"}, 
          React.createElement("span", null, this.props.data.subject)
        ), 
        React.createElement("td", {className: "zb-detail"}, 
          React.createElement(ListDetail, {data: this.props.data, contentType: this.props.contentType})
        )
      )
    );
  }
})

var ListContent = React.createClass({displayName: "ListContent",
  render: function() {
    var self = this;
    var listNodes = this.props.data.map(function(data){
      return (
        React.createElement(ListNode, {data: data, contentType: self.props.contentType})
      );
    });

    return (
      React.createElement("table", {className: "zb-list-content table table-striped", id: 'zb-table-' + self.props.contentType}, 
        React.createElement("thead", {className: "zb-list-head-area"}, 
          React.createElement("tr", {className: "zb-list-head"}, 
            React.createElement("th", {className: "zb-head zb-head-receiver"}, React.createElement("span", null, "Email")), 
            React.createElement("th", {className: "zb-head zb-head-subject"}, React.createElement("span", null, "Subject")), 
            React.createElement("th", {className: "zb-head zb-head-details"}, React.createElement("span", null, "Details"))
          )
        ), 
        React.createElement("tbody", {className: "zb-list-row-area"}, 
        listNodes
        )
      )
    );
  }
});

var SignalApp = React.createClass({displayName: "SignalApp",
  getInitialState: function() {
    return {signals: [], links: [], data: [], _data: [], 
      contentType:'EmailTracked',
      activeTab:'signals', 
      dashboardEnabled: false,
      dashboardAuthenticated: false,
      fixFunctionArea: false,
      toggleDashboardText: 'expand',
      loginHelperText: 'zenblip loading...',
      queryText: '',
      senderEmail: '',
      accessToken:'',
      collapse: false
      }
  },
  componentDidMount: function() {
    //this.loadSignalsFromServer();
    //setInterval
  },
  loadSignalsFromServer: function(callback) {
    var self = this;
    console.log({sender: this.state.senderEmail, access_token: this.state.accessToken});
    //TODO: add csrf token
    $.getJSON(this.props.baseURL + this.props.signalResourcePath, 
      {sender: this.state.senderEmail, access_token: this.state.accessToken}, function(data){
      //console.log(data);
      console.log('loaded');
      signals = data['data']
      self.setState({
        signals: signals,
        _data: signals,
        data: signals,
        contentType: 'EmailTracked'
      });
      self.filterQueryText();
      if(callback && typeof callback == 'function'){
        callback();
      }
    });
  },
  loadLinksFromServer: function(callback) {
    var self = this;
    //TODO: add csrf token
    $.getJSON(this.props.baseURL + this.props.linkResourcePath, 
      {sender: this.state.senderEmail, accessed:true, access_token: this.state.accessToken}, function(data){
      //console.log(data);
      links = data['data']
      self.setState({
        links: links,
        _data: links,
        data: links,
        contentType: 'LinkClicked'
      });
      self.filterQueryText();
      if(callback && typeof callback == 'function'){
        callback();
      }
    });
  },
  allSignals: function(e){
    e && e.preventDefault();
    this.setState({
      _data: this.state.signals,
      data: this.state.signals,
      activeTab: 'signals',
      contentType: 'EmailTracked'
    });
    this.loadSignalsFromServer();
    this.filterQueryText();
  },
  filterOpened: function(e) {
    function compareByLastAccessed (a, b) {
      if(a.modified.timestamp > b.modified.timestamp){
        return -1;
      }
      if(a.modified.timestamp < b.modified.timestamp){
        return 1;
      }
      return 0;
    }
    e && e.preventDefault();
    var data = $.map(this.state.signals, function(signal) {
      if (signal.access_count > 0){
        return signal;  
      }
    });
    data.sort(compareByLastAccessed);
    this.setState({
      _data: data,
      data: data,
      activeTab: 'opened',
      contentType: 'EmailOpened'
    });
    this.filterQueryText();
  },
  filterNotOpened: function(e) {
    e && e.preventDefault();
    var data = $.map(this.state.signals, function(signal) {
      if (signal.access_count == 0){
        return signal;  
      }
    });
    this.setState({
      _data: data,
      data: data,
      activeTab: 'notopened',
      contentType: 'EmailNotOpened'
    });
    this.filterQueryText();
  },
  linksClicked: function(e){
    e && e.preventDefault();
    this.setState({
      data: this.state.links,
      _data: this.state.links,
      activeTab: 'linksClicked',
      contentType: 'LinkClicked'
    });
    this.loadLinksFromServer();
    this.filterQueryText();
  },
  showDashboard: function() {
    var self = this;
    $('#zb-dashboard').stop().animate({
      height: self.props.dashboardHeight
    }, 500, function() {
      self.setState({
        fixFunctionArea: true
      });  
    });
    this.setState({
      dashboardEnabled: true,
      toggleDashboardText: 'shrink'
    }); 
  },
  hideDashboard: function() {
    var self = this;
    $('#zb-dashboard').stop().animate({
      height: 0
    }, 500);
    this.setState({
      dashboardEnabled: false,
      fixFunctionArea: false,
      toggleDashboardText: 'expand'
    });
  },
  toggleDashboard: function(e) {
    e.preventDefault();
    if(!this.state.dashboardEnabled){
      this.showDashboard();      
    }else{
      this.hideDashboard();
    }
  },
  onQuerySubmit:  function(e) {
    e.preventDefault();
    //TODO: send real request
  },
  onQueryChange: function(e) {
    this.setState({
      queryText: e.target.value
    });
    this.filterQueryText(e.target.value);
  },
  onQueryFocus: function(e) {
    e.preventDefault();
    if(!this.state.dashboardEnabled){
      this.showDashboard();  
    }
    this.setState({
      queryFocus: true
    });
  },
  onQueryBlur: function(e) {
    e.preventDefault();
    this.setState({
      queryFocus: false
    });
  },
  filterQueryText: function(queryText) {
    var self = this;
    //console.log('queryText1: ' + queryText);
    //console.log('queryText2: ' + this.state.queryText);
    if(typeof queryText == 'undefined'){
      if(this.state.queryText == ''){
        return;
      }else{
        queryText = this.state.queryText;
      }
    }
    if(queryText == ''){
      this.setState({
        data: this.state._data
      });
      return;
    }
    var data = $.map(this.state._data, function(row) {
      if(row.subject && row.subject.indexOf(queryText) != -1){
        return row;
      }
      //TODO: remove receivers after new data structure row.receiver_emails roll-out
      if(row.receivers && row.receivers.to && Object.keys(row.receivers.to).length >0 &&
       Object.keys(row.receivers.to)[0].indexOf(queryText) != -1){
        return row;
      }
      if(row.receiver_emails){
        for(var k in row.receiver_emails){
          if(row.receiver_emails[k].indexOf(queryText) != -1){
            return row;
          }
        }
      }
      if(row.device && row.device.indexOf(queryText) != -1){
        return row;
      }
      if(row.country && row.country.indexOf(queryText) != -1){
        return row;
      }
    });
    this.setState({
      data: data
    });
  },
  exportCSV: function(e) {
    //return ExcellentExport.csv(e.currentTarget, 'zb-table-'+this.state.contentType);
    var activityReportPath = this.props.activityReportPath || '/activity_report'
    var url = this.props.baseURL + activityReportPath + '?t=' + this.state.accessToken +'&sender='+encodeURIComponent(this.state.senderEmail);
    window.open(url, '_blank');
    return
  },
  refreshDashboardTable: function(e) {
    var self = this;
    e && e.preventDefault();
    switch(this.state.contentType){
      case 'EmailTracked':
        this.allSignals(e);
        break;
      case 'EmailOpened':
        this.loadSignalsFromServer(function() {
          self.filterOpened();
        });
        break;
      case 'EmailNotOpened':
        this.loadSignalsFromServer(function() {
          self.filterNotOpened();
        });
        break;
      case 'linksClicked':
        this.linksClicked(e);
        break;
      default:
        console.log(this.state.contentType);
        break;
    } 
  },
  onAuthenticationFailed: function(setting) {
    var message = setting && setting.message || 'Click here to login zenblip';
    this.setState({
      loginHelperText: message,
      collapse: setting.collapse? true: false
    });
    //TODO: a setting to remove toolbar for free plan
  },
  onLoginClick: function(e) {
    e.preventDefault();
    zenblip.getAndUpdateUserInfo(true);
    this.setState({
      loginHelperText: 'Loading authentication...',
    });
  },
  onAuthenticated: function(setting) {
    console.log('onAuthenticated');
    this.setState({
      dashboardAuthenticated: true,
      senderEmail: setting.senderEmail,
      accessToken: setting.accessToken
    });
    this.loadSignalsFromServer();
  },
  render: function() {
    var self = this;
    var cx = React.addons.classSet;
    var signalsClass = cx({
      'track': true,
      'zb-active': self.state.activeTab == 'signals'
    });
    var signalsOpenedClass = cx({
      'track': true,
      'zb-active': this.state.activeTab == 'opened'
    });
    var signalsNotOpenedClass = cx({
      'track': true,
      'zb-active': this.state.activeTab == 'notopened'
    });
    var linksClickedClass = cx({
      'track': true,
      'zb-active': this.state.activeTab == 'linksClicked'
    });
    var functionAreaClass = cx({
      'zb-function-area': true,
      fixed: this.state.fixFunctionArea
    });
    var toggleDashboardClass = cx({
      'track': true,
      'zb-toggle-dashboard': true,
    });
    var toggleDashboardIconClass = cx({
      'fa': true,
      'zb-white': true,
      'fa-angle-double-down': !this.state.dashboardEnabled,
      'fa-angle-double-up': this.state.dashboardEnabled
    });
    var toolbarDownloadClass = cx({
      'zb-tool': true,
      'zb-display-none': false,
    });
    var toolbarRefreshClass = cx({
      'zb-tool': true,
      'zb-display-none': !this.state.dashboardEnabled,
    });
    var queryIconClass = cx({
      'zb-query-icon': true,
      'zb-transparent': this.state.queryFocus || this.state.queryText.length > 0
    });
    var toolbarClass = cx({
      'zb-toolbar': true,
      'zb-display-none': !this.state.dashboardAuthenticated
    });
    var loginHelperClass = cx({
      'zb-login-helper': true,
      'zb-display-none': this.state.dashboardAuthenticated
    });
    var hideLogoClass = cx({
      'zb-logo': true,
      'zb-hide-logo': this.props.hideLogo
    });
    var dashboardContainerClass = cx({
      'zb-dashboard-container': true,
      'zb-display-none': this.state.collapse
    });
    return (
      React.createElement("div", {className: dashboardContainerClass}, 
        React.createElement("div", {className: "zb-navbar"}, 
          React.createElement("div", {className: "zb-navbar-inner zb-clearfix"}, 
            React.createElement("div", {className: toolbarClass}, 
              React.createElement("a", {className: toggleDashboardClass, href: "#", onClick: this.toggleDashboard, "data-track": "Click Expand Button"}, 
                React.createElement("i", {className: toggleDashboardIconClass}), " ", this.state.toggleDashboardText
              ), 
              React.createElement("a", {className: toolbarDownloadClass, href: "#", onClick: this.exportCSV, title: "download recent activities", "data-track": "Export Dashboard to CSV"}, 
                React.createElement("i", {className: "fa zb-white fa-download"})
              ), 
              React.createElement("a", {className: toolbarRefreshClass, href: "#", onClick: this.refreshDashboardTable, title: "refresh", "data-track": "Refresh Dashobard Table", "data-trackop": "{'type':"+this.state.contentType+"}"}, 
                React.createElement("i", {className: "fa zb-white fa-refresh"})
              ), 
              React.createElement("ul", {className: "zb-nav"}, 
                React.createElement("li", null, 
                  React.createElement("a", {className: "track zb-toggle-menu pull-left", href: "#", onClick: this.toggleDashboard, "data-track": "Click Logo or Detail Icon Button"}, 
                    React.createElement("i", {className: "fa fa-bars zb-white"})
                  ), 
                  React.createElement("a", {className: "track pull-left", href: "http://www.zenblip.com", target: "_blank", "data-track": "Click Logo or Detail Icon Button"}, 
                    React.createElement("img", {className: hideLogoClass, src: "https://s3-ap-northeast-1.amazonaws.com/zenbl/prod/static/zenblip_logo_small.png"})
                  )
                ), 
                React.createElement("li", null, 
                  React.createElement("div", {className: "zb-query-frame"}, 
                    React.createElement("span", {className: queryIconClass}, React.createElement("i", {className: "fa fa-search"})), 
                    React.createElement("form", {onSubmit: this.onQuerySubmit}, 
                      React.createElement("input", {onChange: this.onQueryChange, onFocus: this.onQueryFocus, onBlur: this.onQueryBlur, value: this.state.queryText, 
                      placeholder: "Search recent events", class: "track", "data-track": "Toolbar Search"})
                    )
                  )
                )
              )
            ), 
            React.createElement("div", {className: loginHelperClass}, 
              React.createElement("a", {href: "#", onClick: this.onLoginClick}, this.state.loginHelperText)
            )
          )
        ), 
        
        React.createElement("div", {id: "zb-dashboard", className: "zb-dashboard"}, 
          React.createElement("div", {id: "zb-function-area", className: functionAreaClass}, 
            React.createElement("ul", {className: "zb-function-list zb-nav"}, 
              React.createElement("li", null, 
                React.createElement("a", {className: signalsClass, href: "#", onClick: this.allSignals, "data-track": "Click EmailsTracked"}, 
                  "Emails Tracked", 
                  React.createElement("div", {className: "zb-arrow-right"})
                )
              ), 
              React.createElement("li", null, 
                React.createElement("a", {className: signalsOpenedClass, href: "#", onClick: this.filterOpened, "data-track": "Click EmailsOpened"}, 
                  "Opened", 
                  React.createElement("div", {className: "zb-arrow-right"})
                )
              ), 
              React.createElement("li", null, 
                React.createElement("a", {className: signalsNotOpenedClass, href: "#", onClick: this.filterNotOpened, "data-track": "Click EmailsNotOpened"}, 
                  "Not Opened", 
                  React.createElement("div", {className: "zb-arrow-right"})
                )
              ), 
              React.createElement("li", null, 
                React.createElement("a", {className: linksClickedClass, href: "#", onClick: this.linksClicked, "data-track": "Click LinksClicked"}, 
                  "Links Clicked", 
                  React.createElement("div", {className: "zb-arrow-right"})
                )
              )
            )
          ), 
          React.createElement("div", {className: "zb-content-area"}, 
            React.createElement(ListContent, {data: this.state.data, contentType: this.state.contentType})
          )
        )
      )
    );
  }
});
//download={this.state.contentType + '.csv'} data-trackop={"{'type':"+this.state.contentType+"}"}