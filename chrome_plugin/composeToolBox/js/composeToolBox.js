//require simplemodal.js

var zenblip = (function(zb, $, dbi, React) {

  var trackControlClass = 'zb-track-control';
  var trackInputClass = 'zb-track-input';
  var trackHiddenInputClass = 'zb-track-hidden-input';
  var customString = 'custom';
  //zb.trackStateName = zb.trackStateName || 'zb-track-state';
  zb.composedToolBoxData = zb.composedToolBoxData || 'zb-post-data';

  zb.goTrackState = function($mail) {
    var data = $mail.data(zb.composedToolBoxData) || {};
    data.track_state = "1";
    $mail.data(zb.composedToolBoxData, data)
    $mail.find('.aoO')
      .attr('data-tooltip', 'Send ‪and Track')
      .addClass('zb-btn-activated')
  };

  zb.goUnTrackState = function($mail) {
    var data = $mail.data(zb.composedToolBoxData) || {};
    data.track_state = "0";
    $mail.data(zb.composedToolBoxData, data)
    $mail.find('.aoO')
      .attr('data-tooltip', 'Send ‪without tracking?')
      .removeClass('zb-btn-activated')
      //.end().find("." + trackHiddenInputClass).val("0"); //set hidden track value
  };

  zb.createTrackControl = function($mail, options) {
    var trackByDefault = options.track_by_default;
    var d = new Date()
    var tcid = "" + d.getSeconds() + d.getMilliseconds();
    var $trackControl = $("<span class='"+ trackControlClass +"'>\
      <input id='zb-tcid-"+tcid+"' class='"+trackInputClass+"' type='checkbox'>\
      <label for='zb-tcid-"+tcid+"'>Track</tabel></span>");
    //var $hiddenInput = $("<input class='"+trackHiddenInputClass+"' type='hidden' name='"+zb.trackStateName+"'>");
    $trackControl.find('input').change(function(){
      console.log("checked: " + this.checked);
      if(this.checked === true){
        zb.goTrackState($mail);
      }else{
        zb.goUnTrackState($mail);
      }
    });

    //console.log($mail);
    //init state
    $mail
      //.find('form').append($hiddenInput)
      .end().find('.aWR').css('display', 'none')
      .end().find('.oG').css('display', 'none');
    if(trackByDefault){
      $trackControl.find('input')[0].checked = true; //set trackControl
      zb.goTrackState($mail);
    }else{
      $trackControl.find('input')[0].checked = false; //set trackControl
      zb.goUnTrackState($mail);
    }
    return $trackControl;
  };

  zb.Reminder = function($mail) {
    this.id = "";
    this.$mail = $mail;
    this.option1 = true;
    this.option2 = false;
    this.option3 = false;
    this.option4 = false;
    this.optionCustom = false;
    this.datePicked = 'Select Date';
    this.timerString = "";
    this.ifNoReply = false;
    this.note = "";
  };

  zb.Reminder.prototype.calculateTimerString = function() {
    //console.log("calculateTimerString");
    //
    //Unfortunately there's no databinding for radio group
    //
    // var timerString="";
    // if( this.option1 ){
    //   timerString = "24h"
    // }else if( this.option2){
    //   timerString = ""+3*24+"h"
    // }else if( this.option3){
    //   timerString = ""+7*24+"h"
    // }else if( this.option4){
    //   timerString = "2m"
    // }
    var timerString = $("input[name='reminddatetime-"+this.id+"']:checked").val();
    if(timerString == customString){
      timerString = this.datePicked;
    }
    this.timerString = timerString;
    return timerString;
  };

  zb.Reminder.prototype.update = function() {
    var data = this.$mail.data(zb.composedToolBoxData) || {};
    data.reminder_enabled = "1";
    data.reminder_timer_string = this.timerString;
    data.reminder_if_no_reply = this.ifNoReply? "1":"";
    data.reminder_note = this.note;
    this.$mail.data(zb.composedToolBoxData, data);
    return this;
  };

  zb.Reminder.prototype.clear = function() {
    var data = this.$mail.data(zb.composedToolBoxData) || {};
    data.reminder_enabled = "0";
    data.reminder_timer_string = "";
    data.reminder_if_no_reply = "";
    data.reminder_note = "";
    this.$mail.data(zb.composedToolBoxData, data);
    return this;
  };

  zb.createReminderControl = function($mail, options) {
    var $reminderControl = $("<button class='zb-btn zb-reminder-btn'><i class='fa fa-lightbulb-o'></i> Reminder</button>");
    var reminder = $mail.data('zb-reminder') || new zb.Reminder($mail);
    var mid = $mail.data('mid');
    reminder.id = mid;

    $reminderControl.click(function(e) {
      var $reminderForm = $("\
        <div class='zb-reminder-modal-content'>\
          <div class='zb-re'>\
            <h3>Remind me after:</h3>\
            <form>\
              <div class='zb-re-form'>\
                <div>\
                <input id='option1-"+mid+"' data-key='option1' name='reminddatetime-"+mid+"' value='24h' type='radio'>\
                <label for='option1-"+mid+"'> 24 Hours </label>\
                </div>\
                <div>\
                <input id='option2-"+mid+"' data-key='option2' name='reminddatetime-"+mid+"' value='3d' type='radio'>\
                <label for='option2-"+mid+"'> 3 Days </label>\
                </div>\
                <div>\
                <input id='option3-"+mid+"' data-key='option3' name='reminddatetime-"+mid+"' value='7d' type='radio'>\
                <label for='option3-"+mid+"'> 7 Days </label>\
                </div>\
                <!--div>\
                <input id='option4-"+mid+"' data-key='option4' name='reminddatetime-"+mid+"' value='5m' type='radio'>\
                <label for='option4-"+mid+"'> 5 Minutes (for test) </label>\
                </div-->\
                <div>\
                <input id='option-custom-"+mid+"' data-key='optionCustom' name='reminddatetime-"+mid+"' value='"+customString+"' type='radio'>\
                <label for='option-custom-"+mid+"'> Custom\
                <input\
                  id='datepicker-"+mid+"'\
                  class='zb-datepicker'\
                  name='date'\
                  type='text'\
                  autofocuss\
                  data-key='datePicked'\
                  >\
                </label>\
                <div id='datepicker-container-"+mid+"'></div>\
                </div>\
                <br>\
                <div>\
                <input id='ifnoreply-"+mid+"' data-key='ifNoReply' type='checkbox'>\
                <label for='ifnoreply-"+mid+"'> Notify me only if there is no reply.\
                </div>\
                <div>\
                <h4>Note:</h4>\
                <div class='zb-re-note'>\
                  <textarea data-key='note' cols='40' rows='3' placeholder='Write a memo to be reminded of.'></textarea>\
                </div>\
                </div>\
              </div>\
              <div class='zb-re-tool-bar'>\
                <ul>\
                  <li>\
                    <a href='#' id='zb-re-enable-"+mid+"' class='zb-btn' > Enable Reminder </a>\
                    <!--a href='#' id='zb-re-enable-"+mid+"' class='zb-re-btn zb-re-enable-btn' > Enable Reminder </a-->\
                  </li>\
                  <li>\
                    <a href='#' cid='zb-re-cancel-"+mid+"' class='zb-btn' > Disable Reminder </a>\
                    <!--a href='#' cid='zb-re-cancel-"+mid+"' class='zb-re-btn zb-re-disable-btn' > Disable Reminder </a-->\
                  </li>\
                </ul>\
              </div>\
            </form>\
          </div>\
        </div>");
      dbi.bind($reminderForm, reminder);
      $reminderForm
      .on('click', '.zb-datepicker', function(e) {
        // e.preventDefault();
        var MAX_REMINDER_TIME_IN_DAYS = 21; //server limit 29 days
        var $this = $(this);
        var now = new Date();
        var min = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
        var max = new Date(now.getFullYear(), now.getMonth(), now.getDate() + MAX_REMINDER_TIME_IN_DAYS);
        //console.log(max);
        $this.pickadate({
          format: 'yyyy-mm-dd',
          formatSubmit: 'yyyy-mm-dd', //useless, we don't use the hidden input
          closeOnSelect: true,
          closeOnClear: false,
          container: '#datepicker-container-'+mid,
          min: min,
          max: max,
          clear:'',
          onClose: function() {
            //this is a fix to the databinding
            //TODO: remove this fix after changing databinding
            reminder.datePicked = $this.val();
            reminder.optionCustom = true;
            // document.getElementById('option-custom-'+mid).checked = true;
            //console.log(reminder.datePicked);
          }
        });
      })
      .on('click', '.zb-re-enable-btn', function(e) {
        e.preventDefault();
        var timerString = reminder.calculateTimerString();
        if (timerString != ""){
          $mail.data('zb-reminder', reminder);
          $reminderControl.addClass('zb-btn-activated');
        }
        reminder.update();
        $.modal.close();
      })
      .on('click', '.zb-re-disable-btn', function(e) {
        e.preventDefault();
        reminder.clear();
        $.modal.close();
        $reminderControl.removeClass('zb-btn-activated');
      }).modal();
    });
    return $reminderControl;
  };

  zb.Templar = function($mail) {
    //this is just a shell
    this.$mail = $mail;
    this.tid = '';
    this.subject = '';
    this.body = '';
  };

  zb.Templar.prototype.update = function() {
    var data = this.$mail.data(zb.composedToolBoxData) || {};
    data.templar_id = this.tid;
    this.$mail.data(zb.composedToolBoxData, data);
    return this;
  };

  zb.createTemplarControl = function($mail, options) {
    var $templarControl = $("<button class='zb-btn zb-template-btn'><i class='fa fa-book'></i> Template</button>");
    var templar = $mail.data('zb-templar') || new zb.Templar($mail);
    var mid = $mail.data('mid');

    $templarControl.click(function(e) {

      var $templateForm = $("\
        <div id='zb-templar-"+mid+"' class='zb-templar-modal-content'>\
        </div>");
      $templateForm.modal({onShow: function(dialog) {
          var onTemplarSelected = function(t) {
            $mail.find(".aoT").val(t.subject);
            $mail.find(".Am").html(t.body);
            templar.tid = t.tid;
            templar.update();
            $.modal.close();
          };
          var emailTemplarApp = React.render(
            React.createElement(TemplarApp, {
              templars: [],
              accessToken: options.access_token,
              baseURL: zb.baseURL,
              templarsResourcePath: zb.templarsResourcePath,
              templarResourcePath: zb.templarResourcePath,
              onTemplarSelected: onTemplarSelected,
              owner: options.sender
            }),
              document.getElementById('zb-templar-'+mid)
          );
          emailTemplarApp.loadTemplars();
        }
      });
    });
    return $templarControl;
  };



  zb.composeToolBoxCronJob = function($mail, options) {
    window.setInterval(function() {
      if($mail.find('.aX').is(':visible')){ //has font toolbar
        if($mail.find('.HM').length > 0 || $mail.width() >= 500){ //embedded mail input box or max
          
          $mail.find('.aDg').css({'margin-top': '-63px'});
        }
        $mail.find('.ct-inner').css('height', '82px');
      }else{
        if($mail.find('.HM').length > 0  || $mail.width() >= 500){
          
          $mail.find('.aDg').css({'margin-top': '0'});
        }
        $mail.find('.ct-inner').css('height', '42px');
      }
    }, 300);
  };

  zb.createComposeToolBox = function($mail, options) {
    var $trackControl = zb.createTrackControl($mail, options);
    var $reminderControl = zb.createReminderControl($mail, options);
    var $templarControl = zb.createTemplarControl($mail, options);
    var $toolbox = $("\
        <div class='ct-container'> \
          <div class='ct-inner'> \
            <table> \
              <tbody> \
                <tr> \
                <td class='zb-tracker-td'> \
                </td> \
                <td> \
                </td> \
                <td class='zb-reminder-td'> \
                </td> \
                <td> \
                </td> \
                <td class='zb-template-td'> \
                </td> \
              </tr> \
              </tbody> \
            </table> \
          </div> \
        </div>");

    $toolbox.find('td.zb-tracker-td').append($trackControl);
    if(options.enable_reminder){
      $toolbox.find('td.zb-reminder-td').append($reminderControl);
    }
    $toolbox.find('td.zb-template-td').append($templarControl);

    zb.composeToolBoxCronJob($mail, options);
    return $toolbox;
  };

  zb.addComposeToolBoxToComposingMails = function(options) {
    // var $newMails = $('.AD').not('.zbTracked');
    var $newMails = $('.aoI').not('.zbTracked');
    if($newMails.length == 0){
      return;
    }
    $newMails.addClass('zbTracked').each(function(index, mail){
      var $mail = $(mail);
      var mid = zb.uuid().substr(-8);
      $mail.data('mid', mid);
      $mail.addClass(mid);
      $mail.find('form').append("<input name='mid' type='hidden' value='"+mid+"'>");
      var $toolbox = zb.createComposeToolBox($mail, options);
      // $toolbox.insertBefore($mail.find('table.iN > tbody > tr:last'));
      $mail.find('.aDj').prepend($toolbox);
      if($mail.find('.HM').length > 0){
        //embedded mail input box
        $mail.find('.HE').css({height: '124px'});
      }
    });
  };
return zb;
}(zenblip || {}, jQuery, DataBind, React));