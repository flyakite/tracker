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

TemplarApp = React.createClass({
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
      <div className="zb-et">
        <div className={templarListContainerClass}>
          <TemplarSearchBar filterText={this.state.filterText} onSearchInputChange={this.onSearchInputChange}/>
          <TemplarList 
            templars={this.state.templars}
            filterText={this.state.filterText}
            deleteTemplar={this.deleteTemplar} 
            onTemplarSelected={this.onTemplarSelected} />
          <TemplarToolBar newTemplar={this.newTemplar} />
        </div>
        <TemplarForm 
          showTemplarForm={this.state.showTemplarForm}
          editingTemplar={this.state.editingTemplar} 
          saveTemplar={this.saveTemplar}
          cancelTemplar={this.cancelTemplar}/>
      </div>
    );
  }
});

var TemplarSearchBar = React.createClass({
  onSearchInputChange: function(e) {
    this.props.onSearchInputChange(
      React.findDOMNode(this.refs.searchInput).value
    );    
  },
  render: function() {
    return (
      <div className="zb-et-search-bar">
        <div className="zb-et-search-frame">
          <input 
            type="text" 
            placeholder="search"
            value={this.props.filterText}
            ref="searchInput"
            onChange={this.onSearchInputChange}
            />
        </div>
      </div>
    );
  }
})

var TemplarItem = React.createClass({
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
      <li className="zb-et-item">
        <ul>
          <li className={replyRateClass} title="Reply Rate"><span className="zb-et-item-reply-rate-figure">{replyRate}</span>%</li>
          <li className="zb-et-item-content"  onClick={this.onTemplarSelected}>
            <div className="zb-et-item-subject">
              {this.props.templar.subject && this.props.templar.subject.substr(0, 50)}
            </div>
            <div className="zb-et-item-body">
              {this.props.templar.body && this.props.templar.body.substr(0,50).replace(/<br \/>/g, '\n')}
            </div>
          </li>
          <li className="zb-et-item-function">
            <a href="#" className="zb-et-delete-btn" onClick={this.deleteTemplar}><span title="Delete">{String.fromCharCode(10006)}</span> </a>
          </li>
        </ul>
      </li>
    );
  }

});

var TemplarList = React.createClass({
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
        <TemplarItem templar={t} deleteTemplar={this.deleteTemplar} onTemplarSelected={this.onTemplarSelected}/>
      )
    }.bind(this);

    return (
      <div className="zb-et-list-container">
        <ul>{this.props.templars.map(listTemplar)}</ul>
      </div>
    );
  }
});

var TemplarToolBar = React.createClass({
  newTemplar: function(e) {
    e.preventDefault();
    e.nativeEvent.stopImmediatePropagation();
    this.props.newTemplar(e);
  },
  render: function() {
    return (
      <div className="zb-et-tool-bar">
        <ul>
          <li>
            <a href="#" className="zb-btn zb-btn-blue" onClick={this.newTemplar}> Create Template </a>
          </li>
        </ul>
      </div>
    );
  }
})

var TemplarForm = React.createClass({
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
      <div className={templarFormClass}>
        <div className="zb-et-form-subject">
          <input type="text" placeholder="Subject" ref="subject" value={this.props.editingTemplar.subject} />
        </div>
        <div className="zb-et-form-body">
          <textarea id="" placeholder="Body" cols="30" rows="10" ref="body" value={this.props.editingTemplar.body}/>
        </div>
        <div className="zb-et-tool-bar">
          <ul>
            <li>
              <a href="#" className="zb-btn zb-btn-blue" onClick={this.saveTemplar}> Save </a>
            </li>
            <li>
              <a href="#" className="zb-btn zb-btn-lowkey" onClick={this.cancelTemplar}> Cancel </a>
            </li>
          </ul>
        </div>
      </div>
    );
  }
});

