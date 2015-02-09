var ListDetail = React.createClass({
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
        detail = 'Sent: ' + this.dateObjectToString(this.props.data.created);
        return (
          <span>{detail}</span>
        );
        break;
      case 'EmailOpened':
        locationInfo = this.locationToString() == "" ? "": " Location: " + this.locationToString();
        deviceInfo = this.props.data.device == null ? "": " Device: " + this.props.data.device;
        detail = 'Opened: ' + this.dateObjectToString(this.props.data.modified) + locationInfo + deviceInfo;
        return (
          <span>{detail}</span>
        );
        break;
      case 'EmailNotOpened':
        detail = 'Sent: ' + this.dateObjectToString(this.props.data.created);
        return (
          <span>{detail}</span>
        );
        break;
      case 'LinkClicked':
        locationInfo = this.locationToString() == "" ? "": " Location: " + this.locationToString();
        deviceInfo = this.props.data.device == null ? "": " Device: " + this.props.data.device;
        detail = ' Clicked: ' + this.dateObjectToString(this.props.data.modified) + locationInfo + deviceInfo;
        return (
          <div>
            <span className="zb-link-url">
              <a target="_blank" href={this.props.data.url}>{this.props.data.url.substr(0,50)+'...'}</a>
            </span>
            <span>
              {detail}
            </span>
          </div>
        );
        break;
      default:
        break;
    }
  }
})


var ListNode = React.createClass({
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
      <tr className="zb-list-row">
        <td className="zb-receiver">
          <span>{receiver}</span>
        </td>
        <td className="zb-subject">
          <span>{this.props.data.subject}</span>
        </td>
        <td className="zb-detail">
          <ListDetail data={this.props.data} contentType={this.props.contentType} />
        </td>
      </tr>
    );
  }
})

var ListContent = React.createClass({
  render: function() {
    var self = this;
    var listNodes = this.props.data.map(function(data){
      return (
        <ListNode data={data} contentType={self.props.contentType} />
      );
    });

    return (
      <table className="zb-list-content table table-striped" id={'zb-table-' + self.props.contentType}>
        <thead className="zb-list-head-area">
          <tr className="zb-list-head">
            <th className="zb-head zb-head-receiver"><span>Email</span></th>
            <th className="zb-head zb-head-subject"><span>Subject</span></th>
            <th className="zb-head zb-head-details"><span>Details</span></th>
          </tr>
        </thead>
        <tbody className="zb-list-row-area">
        {listNodes}
        </tbody>
      </table>
    );
  }
});

var SignalApp = React.createClass({
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
      accessToken:''
      }
  },
  componentDidMount: function() {
    //this.loadSignalsFromServer();
    //setInterval
  },
  loadSignalsFromServer: function() {
    var self = this;
    console.log('OKKK');
    console.log({sender: this.state.senderEmail, access_token: this.state.accessToken});
    $.getJSON(this.props.baseURL + this.props.signalResourcePath, 
      {sender: this.state.senderEmail, access_token: this.state.accessToken}, function(data){
      //console.log(data);
      signals = data['data']
      self.setState({
        signals: signals,
        _data: signals,
        data: signals,
        contentType: 'EmailTracked'
      });
      self.filterQueryText();
    });
  },
  loadLinksFromServer: function() {
    var self = this;
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
    });
  },
  allSignals: function(e){
    e.preventDefault();
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
    e.preventDefault();
    var data = $.map(this.state.signals, function(signal) {
      if (signal.access_count > 0){
        return signal;  
      }
    });
    this.setState({
      _data: data,
      data: data,
      activeTab: 'opened',
      contentType: 'EmailOpened'
    });
    this.filterQueryText();
  },
  filterNotOpened: function(e) {
    e.preventDefault();
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
    e.preventDefault();
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
    return ExcellentExport.csv(e.currentTarget, 'zb-table-'+this.state.contentType);
  },
  onAuthenticationFailed: function() {
    this.setState({
      loginHelperText: 'Click here to login zenblip',
    });
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
    return (
      <div className='zb-dashboard-container'>
        <div className="zb-navbar">
          <div className="zb-navbar-inner zb-clearfix">
            <div className={toolbarClass}>
              <a className={toggleDashboardClass} href='#' onClick={this.toggleDashboard} data-track="Click Expand Button">
                <i className={toggleDashboardIconClass}></i> {this.state.toggleDashboardText}
              </a>
              <a className={toolbarDownloadClass} href='#' onClick={this.exportCSV} download={this.state.contentType + '.csv'} title="export to csv" data-track="Export CSV" data-trackop={"{'type':"+this.state.contentType+"}"}>
                <i className="fa zb-white fa-download"></i> 
              </a>
              <ul className="zb-nav">
                <li>
                  <a className={toggleDashboardClass} href='#' onClick={this.toggleDashboard} data-track="Click Logo or Detail Icon Button">
                    <i className="fa fa-bars zb-white"></i>
                    <img className={hideLogoClass} src="https://s3-ap-northeast-1.amazonaws.com/zenbl/prod/static/zenblip_logo_small.png"></img>
                  </a>
                </li>
                <li>
                  <div className='zb-query-frame'>
                    <span className={queryIconClass}><i className='fa fa-search' /></span>
                    <form onSubmit={this.onQuerySubmit}>
                      <input onChange={this.onQueryChange} onFocus={this.onQueryFocus} onBlur={this.onQueryBlur} value={this.state.queryText} 
                      placeholder='Search recent events' class="track" data-track="Toolbar Search"/>
                    </form>
                  </div>
                </li>
                <li>
                  
                </li>
              </ul>
            </div>
            <div className={loginHelperClass}>
              <a href='#' onClick={this.onLoginClick}>{this.state.loginHelperText}</a>
            </div>
          </div>
        </div>
        
        <div id='zb-dashboard' className='zb-dashboard'>
          <div id='zb-function-area' className={functionAreaClass}>
            <ul className='zb-function-list zb-nav'>
              <li>
                <a className={signalsClass} href="#" onClick={this.allSignals} data-track="Click EmailsTracked">
                  Emails Tracked
                  <div className="zb-arrow-right"></div>
                </a>
              </li>
              <li>
                <a className={signalsOpenedClass} href="#" onClick={this.filterOpened} data-track="Click EmailsOpened">
                  Opened
                  <div className="zb-arrow-right"></div>
                </a>
              </li>
              <li>
                <a className={signalsNotOpenedClass} href="#" onClick={this.filterNotOpened} data-track="Click EmailsNotOpened">
                  Not Opened
                  <div className="zb-arrow-right"></div>
                </a>
              </li>
              <li>
                <a className={linksClickedClass} href="#" onClick={this.linksClicked} data-track="Click LinksClicked">
                  Links Clicked
                  <div className="zb-arrow-right"></div>
                </a>
              </li>
            </ul>
          </div>
          <div className="zb-content-area">
            <ListContent data={this.state.data} contentType={this.state.contentType}/>
          </div>
        </div>
      </div>
    );
  }
});