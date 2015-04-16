# -*- coding: utf-8 -*-
'''
Created on 2015/4/8

@author: sushih-wen
'''
import logging
from datetime import datetime, timedelta
from ferris import BasicModel
from google.appengine.ext import ndb
from google.appengine.api import taskqueue


class Reminder(BasicModel):
    sender = ndb.StringProperty(required=True)
    token = ndb.StringProperty(required=True)
    timer_string = ndb.StringProperty()
    if_no_reply = ndb.BooleanProperty()
    note = ndb.TextProperty()
    trigger_datetime = ndb.DateTimeProperty()

    @staticmethod
    def timer_string_to_target_datetime(timer_string):
        """
        2015-4-25
        2016-5-10
        """
        time_buffer_for_gmail_id_creation_in_minutes = 60
        reminder_max_time_in_queue_in_days = 29
        
        now = datetime.utcnow()
        try:
            y, m, d = timer_string.split('-')
            target = datetime(int(y), int(m), int(d), now.hour, now.minute)
            if target <= now + timedelta(minutes=time_buffer_for_gmail_id_creation_in_minutes):
                logging.warn("ReminderTimerLessThanBuffer %s" % timer_string)
                return datetime.utcnow() + timedelta(minutes=time_buffer_for_gmail_id_creation_in_minutes)
            elif target > now + timedelta(reminder_max_time_in_queue_in_days):
                logging.warn("ReminderTimerLargerThanMax %s" % timer_string)
                return datetime.utcnow() + timedelta(days=reminder_max_time_in_queue_in_days)
            else:
                return target
        except:
            logging.exception("ReminderTimerStringException %s" % timer_string)
            return datetime.utcnow() + timedelta(days=1)
        

    @staticmethod
    def timer_string_to_timedelta(timer_string):
        """
        1s = 1 second
        2m = 2 minutes
        3d = 3 days
        24h = 24 hours
        
        """
        
            
        try:
            number, unit = int(timer_string[:-1]), timer_string[-1:]
        except:
            logging.error("FormatIncorrect %s" % timer_string)
            return None
        
        if unit == 's':
            return timedelta(seconds=number)
        elif unit == 'm':
            return timedelta(minutes=number)
        elif unit == 'h':
            return timedelta(hours=number)
        elif unit == 'd':
            return timedelta(days=number)
        else:
            return None

    @classmethod
    def add_reminder_to_taskqueue(cls, timer_string, if_no_reply, note, sender, token):
        
        now = datetime.utcnow()
        if '-' in timer_string:
            trigger_datetime = cls.timer_string_to_target_datetime(timer_string)
        else:
            td = cls.timer_string_to_timedelta(timer_string)
            trigger_datetime = now + td
            
        if not trigger_datetime:
            return
        reminder = cls(
            sender=sender,
            token=token,
            timer_string=timer_string,
            if_no_reply=if_no_reply,
            note=note,
            trigger_datetime=trigger_datetime
        )
        reminder.put()


        taskqueue.add(
            url='/reminders/trigger_reminder',
            method='GET',
            countdown=(trigger_datetime - now).total_seconds(),
            params={'reminder_id': reminder.key.id()}
        )
