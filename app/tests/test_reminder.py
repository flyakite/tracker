# -*- coding: utf-8 -*-
'''
Created on 2015/4/13

@author: sushih-wen
'''
import json
import logging
import base64
from datetime import timedelta, datetime
from uuid import uuid4
from google.appengine.ext import testbed
from ferrisnose import AppEngineTest, AppEngineWebTest, FerrisAppTest
from app.models.signal import Signal
from app.models.reminder import Reminder
from app.models.access import Access
from app.models.user_info import UserInfo
from app.controllers.signals import Signals
from app.controllers.reminders import Reminders
from test_base import TestBase



class TestReminderController(TestBase):

    def setUp(self):
        AppEngineWebTest.setUp(self)
        self.add_controller(Signals) #create signal
        self.add_controller(Reminders)
        self.mail_stub = self.testbed.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def test_timer_string_to_target_datetime(self):
        now = datetime.utcnow()
        
        #common case
        d = now + timedelta(days=1)
        timer_string = '%s-%s-%s' % (d.year, d.month, d.day)
        d = Reminder.timer_string_to_target_datetime(timer_string)
        self.assertGreater(d, datetime(now.year, now.month, now.day + 1))
        self.assertLess(d, datetime(now.year, now.month, now.day + 1, now.hour, now.minute) + timedelta(minutes=10))
        
        #incorrect format
        d = now + timedelta(days=1)
        timer_string = '%s-%s%s' % (d.year, d.month, d.day)
        d = Reminder.timer_string_to_target_datetime(timer_string)
        self.assertGreater(d, datetime(now.year, now.month, now.day + 1))
        self.assertLess(d, datetime(now.year, now.month, now.day + 1, now.hour, now.minute) + timedelta(minutes=10))
        
        #invalid number
        timer_string = '%s-%s-%s' % (now.year, now.month, 500)
        d = Reminder.timer_string_to_target_datetime(timer_string)
        self.assertGreater(d, datetime(now.year, now.month, now.day + 1))
        self.assertLess(d, datetime(now.year, now.month, now.day + 1, now.hour, now.minute) + timedelta(minutes=10))
        
        #long period
        d = now + timedelta(days=2000)
        timer_string = '%s-%s-%s' % (d.year, d.month, d.day)
        d = Reminder.timer_string_to_target_datetime(timer_string)
        self.assertGreater(d, datetime(now.year, now.month, now.day))
        

    def test_timer_string_to_timedelta(self):
        timer_string = '24h'
        t = Reminder.timer_string_to_timedelta(timer_string)
        self.assertEqual(t, timedelta(hours=24))
        timer_string = '24m'
        t = Reminder.timer_string_to_timedelta(timer_string)
        self.assertEqual(t, timedelta(minutes=24))
        timer_string = '24s'
        t = Reminder.timer_string_to_timedelta(timer_string)
        self.assertEqual(t, timedelta(seconds=24))
        timer_string = '24d'
        t = Reminder.timer_string_to_timedelta(timer_string)
        self.assertEqual(t, timedelta(days=24))

    def test_add_reminder_to_taskqueue(self):
        token = 'token_12345'
        sender = 'user1@asdf.com'
        Reminder.add_reminder_to_taskqueue('2h', True, 'note', sender, token)
        r = Reminder.find_by_properties(token=token)
        self.assertEqual(r.sender, sender)
        self.assertEqual(r.if_no_reply, True)
        self.assertEqual(r.note, 'note')
        self.assertGreaterEqual(r.trigger_datetime, datetime.utcnow() + timedelta(minutes=120-1))
        self.assertLessEqual(r.trigger_datetime, datetime.utcnow() + timedelta(minutes=120))
        
        d = datetime.now() + timedelta(days=2000)
        timer_string = '%s-%s-%s' % (d.year, d.month, d.day)
        Reminder.add_reminder_to_taskqueue(timer_string, True, 'note', sender, token)
        
    def test_trigger_reminder(self):
        sender = 'user1@asdf.com'
        signal = self.create_signal(sender, 'subject', 'to_user@asdf.com')
        reminder = Reminder(token=signal.token,
                            sender=sender,
                            if_no_reply=False,
                            note='note',
                            timer_string='2h',
                            trigger_datetime=datetime.utcnow()
                            )
        reminder.put()
        r = Reminder.get_by_id(int(reminder.key.id()))
        assert r
        r = self.testapp.post('/reminders/trigger_reminder', {'reminder_id': reminder.key.id()})
        self.assertEqual(r.status_code, 200)
        
        messages = self.mail_stub.get_sent_messages(to=sender)
        self.assertEqual(1, len(messages))
        self.assertEqual(sender, messages[0].to)