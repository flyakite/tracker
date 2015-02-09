var Link = React.createClass({displayName: "Link",
  render: function() {
    return (
      React.createElement("li", {className: "link"}, 
        React.createElement("a", {className: "url", href: this.props.link.url, target: "_blank"}, 
          this.props.link.url
        )
      )
    );
  }
})

var LinkList = React.createClass({
  displayName: 'LinkList',
  render: function() {
    // console.log(this.data);
    var linkNodes = this.props.data.map(function(link){
      return (
        React.createElement(Link, {link: link})
      );
    });
    return (
      React.createElement("ul", {className: "linkList"}, 
        linkNodes
      )
    );
  }
});

var Signal = React.createClass({displayName: "Signal",
  render: function() {
    var receiver;
    if( this.props.signal.receivers.to != null ){
      receiver = Object.keys(this.props.signal.receivers.to)[0]
    }
    return (
      React.createElement("li", {className: "signal"}, 
        React.createElement("span", {className: "receiver"}, 
          receiver
        ), 
        React.createElement("span", {className: "subject"}, 
          this.props.signal.subject
        )
      )
    );
  }
})

var SignalList = React.createClass({
  displayName: 'SignalList',
  render: function() {
    // console.log(this.data);
    var signalNodes = this.props.data.map(function(signal){
      return (
        React.createElement(Signal, {signal: signal})
      );
    });

    return (
      React.createElement("ul", {className: "signalList"}, 
        signalNodes
      )
    );
  }
});

var ListContent = React.createClass({displayName: "ListContent",
  render: function() {
    console.log('contentType: ' +this.props.contentType);
    switch(this.props.contentType){
      case 'SignalList':
        return (
          React.createElement(SignalList, {data: this.props.data})
        );
        break;

      case 'LinkList':
        return (
          React.createElement(LinkList, {data: this.props.data})
        );
        break;

      default:
        return (
          React.createElement("div", null)
        );
        break;
    }
  }
});

var SignalApp = React.createClass({displayName: "SignalApp",
  loadSignalsFromServer: function() {
    var self = this;
    $.getJSON(this.props.baseURL + this.props.signalResourcePath, {sender: this.props.senderEmail}, function(data){
      console.log(data);
      signals = data['data']
      self.setState({
        signals: signals,
        data: signals,
        contentType: 'SignalList'
      });
    })
  },
  loadLinksFromServer: function() {
    var self = this;
    $.getJSON(this.props.baseURL + this.props.linkResourcePath, {sender: this.props.senderEmail, accessed:true}, function(data){
      console.log(data);
      links = data['data']
      self.setState({
        links: links,
        data: links,
        contentType: 'LinkList'
      });
    })
  },
  getInitialState: function() {
    return {signals: [], links: [], data: [], contentType:'SignalList',
      activeTab:'signals', 
      dashboardEnabled: false,
      fixFunctionArea: false
      }
  },
  componentDidMount: function() {
    this.loadSignalsFromServer();
    //setInterval
  },
  allSignals: function(e){
    e.preventDefault();
    this.setState({
      data: this.state.signals,
      activeTab: 'signals',
      contentType: 'SignalList'
    });
    this.loadSignalsFromServer();
  },
  filterOpened: function(e) {
    e.preventDefault();
    var data = $.map(this.state.signals, function(signal) {
      if (signal.access_count > 0){
        return signal;  
      }
    });
    this.setState({
      data: data,
      activeTab: 'opened',
      contentType: 'SignalList'
    });
  },
  filterNotOpened: function(e) {
    e.preventDefault();
    var data = $.map(this.state.signals, function(signal) {
      if (signal.access_count == 0){
        return signal;  
      }
    });
    this.setState({
      data: data,
      activeTab: 'notopened',
      contentType: 'SignalList'
    });
  },
  linksClicked: function(e){
    e.preventDefault();
    this.setState({
      data: this.state.links,
      activeTab: 'linksClicked',
      contentType: 'LinkList'
    });
    this.loadLinksFromServer();
  },
  toggleDashboard: function(e) {
    e.preventDefault();
    var self = this;
    if(!this.state.dashboardEnabled){
      $('#zenblip-dashboard').stop().animate({
        height: '300px'
      }, 500, function() {
        self.setState({
          fixFunctionArea: true
        });  
      });
      self.setState({
        dashboardEnabled: true
      });  
      
    }else{
      $('#zenblip-dashboard').stop().animate({
        height: 0
      }, 500);
      this.setState({
        dashboardEnabled: false,
        fixFunctionArea: false
      });
    }
  },
  render: function() {
    var self = this;
    var cx = React.addons.classSet;
    var signalsClass = cx({
      active: self.state.activeTab == 'signals'
    });
    var signalsOpenedClass = cx({
      active: this.state.activeTab == 'opened'
    });
    var signalsNotOpenedClass = cx({
      active: this.state.activeTab == 'notopened'
    });
    var linksClickedClass = cx({
      active: this.state.activeTab == 'linksClicked'
    });
    var functionAreaClass = cx({
      'function-area': true,
      fixed: this.state.fixFunctionArea
    });
    var toggleDashboardClass = cx({
      'toggle-dashboard': true,
      solid: this.state.dashboardEnabled
    });
    
    return (
      React.createElement("div", null, 
        React.createElement("div", {className: "toggle-dashboard"}, 
          React.createElement("a", {className: toggleDashboardClass, href: "#", onClick: this.toggleDashboard}, "toggle")
        ), 
        React.createElement("div", {id: "zenblip-dashboard", className: "dashboard"}, 
          React.createElement("div", {id: "zenblip-function-area", className: functionAreaClass}, 
            React.createElement("ul", {className: "function-list"}, 
              React.createElement("li", null, 
                React.createElement("a", {className: signalsClass, href: "#", onClick: this.allSignals}, 
                  "Tracked", 
                  React.createElement("div", {className: "arrow-right"})
                )
              ), 
              React.createElement("li", null, 
                React.createElement("a", {className: signalsOpenedClass, href: "#", onClick: this.filterOpened}, 
                  "Opened", 
                  React.createElement("div", {className: "arrow-right"})
                )
              ), 
              React.createElement("li", null, 
                React.createElement("a", {className: signalsNotOpenedClass, href: "#", onClick: this.filterNotOpened}, 
                  "Not Opened", 
                  React.createElement("div", {className: "arrow-right"})
                )
              ), 
              React.createElement("li", null, 
                React.createElement("a", {className: linksClickedClass, href: "#", onClick: this.linksClicked}, 
                  "Links Clicked", 
                  React.createElement("div", {className: "arrow-right"})
                )
              )
            )
          ), 
          React.createElement("div", {className: "content-area"}, 
            React.createElement(ListContent, {data: this.state.data, contentType: this.state.contentType})
          )
        )
      )
    );
  }
});