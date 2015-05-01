# -*- coding: utf-8 -*-
'''
Created on 2015/4/8

@author: sushih-wen
'''
import json
import re
import logging
import cPickle as pickle
import base64
import zlib
import Crypto.Cipher.AES
from datetime import datetime, timedelta
from email.utils import parseaddr
from libs.pkcs7 import PKCS7Encoder
from uuid import uuid4
from urllib import urlencode
from google.appengine.api import users, urlfetch, memcache
from google.appengine.ext import deferred, ndb
from google.appengine.ext.db import TransactionFailedError
from ferris import Controller, route_with, scaffold
from ferris.core import mail
from app.models.signal import Signal
from app.models.access import Access
from app.models.user_info import UserInfo
from app.models.user_track import UserTrack
from app.models.link import Link
from app.models.reminder import Reminder
from app.models.statistic import Statistic
from app.utils import is_email_valid, is_user_legit
from app.controllers.base import BaseController
from app.libs.google_client import GoogleMessageClient


class Reminders(BaseController):

    @route_with('/reminders/trigger_reminder')
    def trigger_reminder(self):
        self.meta.change_view('json')

        self.context['message'] = ""
        reminder_id = self.request.get('reminder_id')
        if not reminder_id:
            logging.error('trigger_reminderMissingReminderID')
            return
        reminder_id = int(reminder_id)
        reminder = Reminder.get_by_id(reminder_id)
        if not reminder:
            logging.error('NoReminder %s' % reminder_id)
            return
        logging.info('Reminder token: %s' % reminder.token)
        signal = Signal.find_by_properties(token=reminder.token, sender=reminder.sender)
        if not signal:
            logging.error('NoSignal %s' % reminder.token)
            return

        if reminder.if_no_reply:  # trigger if no reply
            if signal.has_reply(update_signal=True):
                logging.info('has reply')
                return

        signal.created = signal.created - timedelta()
        args = [reminder.sender, "[zenblip Reminder] " + signal.subject]
        kwargs = dict(template_name='trigger_reminder',
                      context={'signal': signal,
                               'reminder': reminder,
                               'message': self.context['message']})

        mail.send_template(*args, **kwargs)

    


