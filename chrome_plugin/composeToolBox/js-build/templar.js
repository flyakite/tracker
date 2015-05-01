var cx = React.addons.classSet;
var defaultTemplars = [{
  tid: 'test1',
  subject:'This is an example template',
  body: "Reply rate will be shown upon enough statistics.",
  owner: '',
  used_times: 0,
  replied_times: 0,
  opened_times: 0
}];

TemplarApp = React.createClass({displayName: "TemplarApp",
  getInitialState: function(){
    return {
      templars: this.props.templars,
      filterText: '',      
      editingTemplar: {},
      showTemplarForm: false,
      showTemplarListContainer: true
    };
  },
  loadTemplars: function() {
    console.dir(this.props.owner);
    $.getJSON(this.props.baseURL + this.props.templarsResourcePath, {
      owner: this.props.owner.email,
      access_token: this.props.accessToken}, function(data) {
      console.log(data);
      if(data && data.data && !data.error){
        if(data.data.length > 0){
          this.setState({
            templars: data.data});
        }else{
          this.setState({
            templars: defaultTemplars});
        }
      }else{
        this.setState({
          templars: defaultTemplars});
      }
    }.bind(this));
  },
  onTemplarSelected: function(t) {
    this.props.onTemplarSelected(t)
  },
  onSearchInputChange: function(text) {
    this.setState({
      filterText: text
    });
  },
  newTemplar: function(e){
    this.setState({
      showTemplarForm: true,
      showTemplarListContainer: false
    })
  },
  saveTemplar: function(templar){
    console.log(templar);
    var tid = 'tid-' + Math.random() * 99999999;
    templar.tid = tid;
    this.setState({
      templars: this.state.templars.concat([templar]),
      showTemplarForm: false,
      showTemplarListContainer: true
    });
    //TODO: sync server
    console.log('post to' + this.props.baseURL + this.props.templarResourcePath);
    $.post(this.props.baseURL + this.props.templarResourcePath, {
        owner: this.props.owner.email,
        action: 'create',
        subject: templar.subject, 
        body: templar.body,
        access_token: this.props.accessToken}, function(data) {
      console.log(data);
      if(data && !data.error){
        this.deleteTemplar(tid);
        this.setState({
          templars: this.state.templars.concat([data]),
        });
      }
    }.bind(this));
  },
  cancelTemplar: function() {
    this.setState({
      showTemplarForm: false,
      showTemplarListContainer: true
    })
  },
  deleteTemplar: function(tid) {
    console.log(tid);
    this.state.templars.forEach(function(t, i) {
      if(t.tid === tid){
        var templars = this.state.templars;
        templars.splice(i, 1);
        this.setState({
          templars: templars
        });
        return;
      }
    }.bind(this));

    $.post(this.props.baseURL + this.props.templarResourcePath, {
      action: 'delete',
      owner: this.props.owner.email,
      tid: tid,
      access_token: this.props.accessToken
    }, function(data) {
      if(data && data.error){
        //TODO: rollback templars
      }
    });
  },
  render: function(){
    var templarListContainerClass = cx({
      'zb-display-none': !this.state.showTemplarListContainer
    });

    return (
      React.createElement("div", {className: "zb-et"}, 
        React.createElement("div", {className: templarListContainerClass}, 
          React.createElement(TemplarSearchBar, {filterText: this.state.filterText, onSearchInputChange: this.onSearchInputChange}), 
          React.createElement(TemplarList, {
            templars: this.state.templars, 
            filterText: this.state.filterText, 
            deleteTemplar: this.deleteTemplar, 
            onTemplarSelected: this.onTemplarSelected}), 
          React.createElement(TemplarToolBar, {newTemplar: this.newTemplar})
        ), 
        React.createElement(TemplarForm, {
          showTemplarForm: this.state.showTemplarForm, 
          editingTemplar: this.state.editingTemplar, 
          saveTemplar: this.saveTemplar, 
          cancelTemplar: this.cancelTemplar})
      )
    );
  }
});

var TemplarSearchBar = React.createClass({displayName: "TemplarSearchBar",
  onSearchInputChange: function(e) {
    this.props.onSearchInputChange(
      React.findDOMNode(this.refs.searchInput).value
    );    
  },
  render: function() {
    return (
      React.createElement("div", {className: "zb-et-search-bar"}, 
        React.createElement("div", {className: "zb-et-search-frame"}, 
          React.createElement("input", {
            type: "text", 
            placeholder: "search", 
            value: this.props.filterText, 
            ref: "searchInput", 
            onChange: this.onSearchInputChange}
            )
        )
      )
    );
  }
})

var TemplarItem = React.createClass({displayName: "TemplarItem",
  onTemplarSelected: function(e) {
    console.log('onTemplarSelected')
    e.preventDefault();
    e.nativeEvent.stopImmediatePropagation();
    this.props.onTemplarSelected(
      this.props.templar
    );
  },
  deleteTemplar: function(e) {
    e.preventDefault();
    e.nativeEvent.stopImmediatePropagation();
    if(confirm("Are you sure you want to delete this template?")){
      console.log(this.props.templar.tid);
      this.props.deleteTemplar(
        this.props.templar.tid
      );
    }

  },
  render: function() {
    var t = this.props.templar;
    var replyRate = "";
    console.log(t);
    if(t && t.used_times > 0){
      replyRate = 100.0 * t.replied_times / t.used_times;
      replyRate = parseInt(replyRate + 0.5);
      replyRate = replyRate > 100 ? 100 : replyRate;
    }

    var replyRateClass = cx({
      "zb-et-item-reply-rate": true,
      "zb-invisible": t.used_times < 10
    });

    return (
      React.createElement("li", {className: "zb-et-item"}, 
        React.createElement("ul", null, 
          React.createElement("li", {className: replyRateClass, title: "Reply Rate"}, React.createElement("span", {className: "zb-et-item-reply-rate-figure"}, replyRate), "%"), 
          React.createElement("li", {className: "zb-et-item-content", onClick: this.onTemplarSelected}, 
            React.createElement("div", {className: "zb-et-item-subject"}, 
              this.props.templar.subject && this.props.templar.subject.substr(0, 50)
            ), 
            React.createElement("div", {className: "zb-et-item-body"}, 
              this.props.templar.body && this.props.templar.body.substr(0,50).replace(/<br \/>/g, '\n')
            )
          ), 
          React.createElement("li", {className: "zb-et-item-function"}, 
            React.createElement("a", {href: "#", className: "zb-et-delete-btn", onClick: this.deleteTemplar}, React.createElement("span", {title: "Delete"}, String.fromCharCode(10006)), " ")
          )
        )
      )
    );
  }

});

var TemplarList = React.createClass({displayName: "TemplarList",
  deleteTemplar: function(tid) {
    this.props.deleteTemplar(tid);
  },
  onTemplarSelected: function(t) {
    this.props.onTemplarSelected(t);
  },
  render: function(){
    //console.log(this.props.templars);
    var listTemplar = function(t, i) {
      console.log(t);
      if(typeof t === 'undefined')
        return
      var filterText = this.props.filterText.toLowerCase();
      if(t.subject.toLowerCase().indexOf(filterText) === -1 && t.body.toLowerCase().indexOf(filterText) === -1){
        return;
      }
      return (
        React.createElement(TemplarItem, {templar: t, deleteTemplar: this.deleteTemplar, onTemplarSelected: this.onTemplarSelected})
      )
    }.bind(this);

    return (
      React.createElement("div", {className: "zb-et-list-container"}, 
        React.createElement("ul", null, this.props.templars.map(listTemplar))
      )
    );
  }
});

var TemplarToolBar = React.createClass({displayName: "TemplarToolBar",
  newTemplar: function(e) {
    e.preventDefault();
    e.nativeEvent.stopImmediatePropagation();
    this.props.newTemplar(e);
  },
  render: function() {
    return (
      React.createElement("div", {className: "zb-et-tool-bar"}, 
        React.createElement("ul", null, 
          React.createElement("li", null, 
            React.createElement("a", {href: "#", className: "zb-btn", onClick: this.newTemplar}, " Create Template ")
          )
        )
      )
    );
  }
})

var TemplarForm = React.createClass({displayName: "TemplarForm",
  saveTemplar: function(e){
    e.preventDefault();
    e.nativeEvent.stopImmediatePropagation();
    var body = React.findDOMNode(this.refs.body).value;
    console.log(body);
    body = body.replace(/(?:\r\n|\r|\n)/g, '<br />');
    this.props.saveTemplar({
      subject: React.findDOMNode(this.refs.subject).value,
      body: body,
      used_times: 0,
      replied_times: 0,
      opened_times: 0
    });
  },
  cancelTemplar: function(e){
    e.preventDefault();
    e.nativeEvent.stopImmediatePropagation();
    this.props.cancelTemplar();
  },
  render: function(){
    var templarFormClass = cx({
      'zb-et-form': true,
      'zb-display-none': !this.props.showTemplarForm
    });
    return (
      React.createElement("div", {className: templarFormClass}, 
        React.createElement("div", {className: "zb-et-form-subject"}, 
          React.createElement("input", {type: "text", placeholder: "Subject", ref: "subject", value: this.props.editingTemplar.subject})
        ), 
        React.createElement("div", {className: "zb-et-form-body"}, 
          React.createElement("textarea", {id: "", placeholder: "Body", cols: "30", rows: "10", ref: "body", value: this.props.editingTemplar.body})
        ), 
        React.createElement("div", {className: "zb-et-tool-bar"}, 
          React.createElement("ul", null, 
            React.createElement("li", null, 
              React.createElement("a", {href: "#", className: "zb-btn", onClick: this.saveTemplar}, " Save ")
            ), 
            React.createElement("li", null, 
              React.createElement("a", {href: "#", className: "zb-btn", onClick: this.cancelTemplar}, " Cancel ")
            )
          )
        )
      )
    );
  }
});

