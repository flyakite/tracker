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
from ferris import settings

WE_HAVE_NO_EMAIL_AUTHORITY_MESSAGE = "We have no authority to check who replied your email."


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
            if self.signal_has_reply(signal, reminder):
                logging.info('has reply')
                return

        signal.created = signal.created - timedelta()
        args = [reminder.sender, "[zenblip Reminder] " + signal.subject]
        kwargs = dict(template_name='trigger_reminder',
                      context={'signal': signal,
                               'reminder': reminder,
                               'message': self.context['message']})

        mail.send_template(*args, **kwargs)

    def signal_has_reply(self, signal, reminder):
        user_info = UserInfo.find_by_properties(email=reminder.sender)
        user_google_id = user_info.google_id
        refresh_token = user_info.refresh_token
        if refresh_token and user_google_id:
            try:
                client = GoogleMessageClient(user_info=user_info)
                thread_id = client.get_message_thread_id(signal.gmail_id)
                logging.info(thread_id)
                threads = client.get_threads(thread_id)
#                 logging.info(threads)
                messages = client.get_messages_from_threads(threads)
                logging.info(messages)
                email = signal.receiver_emails[0]
                logging.info('check replies from %s' % email)
                replies = replies_from_email_after_message_id(email, signal.gmail_id, messages)
                logging.info(replies)
                if replies:
                    logging.info('has replies')
                    return True
                else:
                    logging.info('no replies')
                    return False
            except Exception as ex:
                logging.exception(ex)
                return False
        else:
            logging.error(
                'trigger_reminder missing parms Error sender: %s google_id: %s refresh_token:%s' %
                (reminder.sender, refresh_token, user_google_id))
            self.context['message'] = WE_HAVE_NO_EMAIL_AUTHORITY_MESSAGE
            return False


def replies_from_email_after_message_id(email, message_id, messages):
    """
    messages : {
        historyId:
        id:
        labelIds:
        payload:
            body:
            filename:
            headers: [
                {
                    "name": "Received",
                    "value": "by 10.229.181.197 with HTTP; Sat, 4 Apr 2015 11:54:13 -0700 (PDT)"
                },
                {
                    "name": "From",
                    "value": "Shih-Wen Su <ck890358@gmail.com>"
                },
                ...
            ],
            "mimeType": "multipart/alternative",
            ...
    }
    """
    logging.info("email %s" % email)
    
    history_id = 0
    for m in messages:
        if m['id'] == message_id:
            try:
                history_id = int(m.get('historyId', 0))
            except:
                logging.exception("history_id")
                history_id = 0
            break
            
    replies = []
    for m in messages:
        try:
            hid = int(m['historyId'])
            if hid < history_id:
                #this history id of the replies must be greater or equal to the sent email
                continue
            payload = m['payload']
            headers = payload['headers']
            for h in headers:
                logging.info(h)
                if h['name'].lower() == "from" and "<%s>" % email in h['value']:
                    logging.info(h['value'])
                    replies.append(m)
                    break
        except:
            logging.exception("replies_from_email_after_message_id")
            continue
            
    return replies
