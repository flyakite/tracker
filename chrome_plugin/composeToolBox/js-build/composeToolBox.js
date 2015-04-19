//require simplemodal.js

var zenblip = (function(zb, $, dbi) {

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
        <div class='basic-modal-content'>\
          <h3>Remind me after:</h3>\
            <form>\
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
              <h4>Note: </h4>\
              <textarea data-key='note' cols='40' rows='3'></textarea>\
              </div>\
              <button id='enable-"+mid+"' class='zb-btn zb-enable-reminder'>Enable Reminder</button>\
              <button id='cancel-"+mid+"' class='zb-btn zb-cancel-reminder'>Disable Reminder</button>\
            </form>\
          <p></p>\
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
      .on('click', '.zb-enable-reminder', function(e) {
        e.preventDefault();
        var timerString = reminder.calculateTimerString();
        if (timerString != ""){
          $mail.data('zb-reminder', reminder);
          $reminderControl.addClass('zb-btn-activated');
        }
        reminder.update();
        $.modal.close();
      })
      .on('click', '.zb-cancel-reminder', function(e) {
        e.preventDefault();
        reminder.clear();
        $.modal.close();
        $reminderControl.removeClass('zb-btn-activated');
      }).modal();
    });
    return $reminderControl;
  };

  zb.Template = function() {
    this.id = "";
    this.name = "";
  };

  zb.createTemplateControl = function($mail, options) {
    var $templateControl = $("<button class='zb-btn zb-template-btn'><i class='fa fa-book'></i> Template</button>");
    var template = $mail.data('zb-template') || new zb.Template($mail);
    var mid = $mail.data('mid');
    template.id = mid;

    $templateControl.click(function(e) {
      var $templateForm = $("\
        <div class='basic-modal-content'>\
          <h3>Save this email as a template</h3>\
          <p>\
            <form>\
              <div>\
              <label for='template-name-"+mid+"'>Template name: </label>\
              <input id='template-name-"+mid+"' data-key='name' value='' name='name' type='text'>\
              </div>\
              <br>\
              <button id='enable-"+mid+"' class='zb-btn zb-save-template'>Save Template</button>\
            </form>\
          </p>\
          <br>\
          <br>\
          <h3>Load a Template</h3>\
          <p>\
            <form>\
              <div>\
                <select id='template-select-"+mid+"'>\
                  <option value='1'>Product introduction</option>\
                  <option value='2'>Subscription enabled</option>\
                  <option value='3'>Follow up 1</option>\
                  <option value='4'>Follow up 2</option>\
                  <option value='5'>Follow up 3</option>\
                  <option value='6'>Thank you letter</option>\
                </select>\
              </div>\
              <br>\
              <button id='cancel-"+mid+"' class='zb-btn zb-load-template'>Load Template</button>\
            </form>\
          </p>\
          <p></p>\
        </div>");
      //dbi.bind($reminderForm, reminder);
      $templateForm
      .find('.zb-save-template')
      .on('click', function(e) {
        e.preventDefault();
        $.modal.close();
      }).end().find('.zb-load-template')
      .on('click', function(e) {
        e.preventDefault();
        var tval = $('#template-select-' + mid).val();
        var newBody = EBody[tval];
        $mail.find(".Am").html(newBody);
        $.modal.close();
      }).end().modal();
    });
    return $templateControl;
  };

  var EBody = {
    1: "<div>Hi ,<br><br> This is a test for zenblip template 1. <br><br>Thank you for Lorem ipsum dolor sit amet, consectetur adipisicing elit. Alias dolorum natus vitae sint quo repudiandae ratione assumenda fugit! A voluptate totam exercitationem aliquam, debitis id voluptas libero aliquid officia porro.</div>",
    2: "<div>Hi ,<br><br> This is a test for zenblip template 2. <br><br>Thank you for Lorem ipsum dolor sit amet, consectetur adipisicing elit. Alias dolorum natus vitae sint quo repudiandae ratione assumenda fugit! A voluptate totam exercitationem aliquam, debitis id voluptas libero aliquid officia porro.</div>",
    3: "<div>Hi ,<br><br> This is a test for zenblip template 3. <br><br>Thank you for Lorem ipsum dolor sit amet, consectetur adipisicing elit. Alias dolorum natus vitae sint quo repudiandae ratione assumenda fugit! A voluptate totam exercitationem aliquam, debitis id voluptas libero aliquid officia porro.</div>",
    4: "<div>Hi ,<br><br> This is a test for zenblip template 4. <br><br>Thank you for Lorem ipsum dolor sit amet, consectetur adipisicing elit. Alias dolorum natus vitae sint quo repudiandae ratione assumenda fugit! A voluptate totam exercitationem aliquam, debitis id voluptas libero aliquid officia porro.</div>",
    5: "<div>Hi ,<br><br> This is a test for zenblip template 5. <br><br>Thank you for Lorem ipsum dolor sit amet, consectetur adipisicing elit. Alias dolorum natus vitae sint quo repudiandae ratione assumenda fugit! A voluptate totam exercitationem aliquam, debitis id voluptas libero aliquid officia porro.</div>",
    6: "<div>Hi ,<br><br> This is a test for zenblip template 6. <br><br>Thank you for Lorem ipsum dolor sit amet, consectetur adipisicing elit. Alias dolorum natus vitae sint quo repudiandae ratione assumenda fugit! A voluptate totam exercitationem aliquam, debitis id voluptas libero aliquid officia porro.</div>"
  }

  zb.createComposeToolBox = function($mail, options) {
    var $trackControl = zb.createTrackControl($mail, options);
    var $reminderControl = zb.createReminderControl($mail, options);
    var $templateControl = zb.createTemplateControl($mail, options);
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
    $toolbox.find('td.zb-reminder-td').append($reminderControl);
    //$toolbox.find('td.zb-template-td').append($templateControl);
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
    });
  };
return zb;
}(zenblip || {}, jQuery, DataBind));