# -*- coding: utf-8 -*-
'''
Created on 2014/8/5

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
from google.appengine.api import users, urlfetch, memcache, taskqueue
from google.appengine.ext import deferred, ndb
from google.appengine.ext.db import TransactionFailedError
from ferris import Controller, route_with, scaffold
from ferris import settings
from app.models.signal import Signal
from app.models.access import Access
from app.models.user_info import UserInfo
from app.models.user_track import UserTrack
from app.models.link import Link
from app.models.reminder import Reminder
from app.models.statistic import Statistic
from accesses import Accesses
from app.utils import is_email_valid, is_user_legit
from app.libs.google_client import GoogleMessageClient

# encrypt secret
# RFC_PASSWORD = "mS3S7HvYgijDGRmKfUD0DxiaUCrPBhdd6yz73zQol5o="
# RFC_SALT = "GknEmuEukOHW0Eor+DTFsA=="
RFC_PASSWORD = "PSCIQGfoZidjEuWtJAdn1JGYzKDonk9YblI0uv96O8s="
RFC_SALT = "ehjtnMiGhNhoxRuUzfBOXw=="


def seperate_email_and_name(mail_string):
    """
    1. ld@ab.com
    2. ld@ab.com,
    3. Leo Del <ld@ab.com>
    4. "Leo Del" <ld@ab.com>

    return {email: name}
    """
    mail_string = mail_string.strip().rstrip(',')

    if not mail_string:
        return None

    name, email = parseaddr(mail_string)
    if email and is_email_valid(email):
        return {email: name}

    if mail_string.endswith('>'):
        m = re.match(r'\"(.*?)\"\s*\<(.*)\>', mail_string, re.UNICODE)
        if not m:
            m = re.match(r'(.*?)\s*\<(.*)\>', mail_string, re.UNICODE)
        if m and is_email_valid(m.group(2)):
            return {m.group(2): m.group(1)}
        else:
            logging.warning("Invalid email string: %s" % mail_string)
            return None
    elif is_email_valid(mail_string):
        return {mail_string.strip(): ''}
    else:
        logging.warning("Invalid email string2: %s" % mail_string)
        return None


def decode_cipher(encrypted):
    """
    deprecated
    """
    password = base64.b64decode(RFC_PASSWORD)
    salt = base64.b64decode(RFC_SALT)
    aes = Crypto.Cipher.AES.new(password, Crypto.Cipher.AES.MODE_CBC, salt)
    padding_encoder = PKCS7Encoder()
    cipher = base64.b64decode(encrypted)
    padded = aes.decrypt(cipher)
    in_utf16 = padding_encoder.decode(padded)
    return in_utf16.decode('utf-16')


class Signals(Accesses):  # TODO: bad inheritance

    @route_with('/signals/debug')
    def debug(self):
        self.meta.change_view('json')
        self._enable_cors()

        if self.request.method != 'POST':
            self.response.status_code = 403
            return

        logging.info(self.request.headers.keys())
        logging.info(self.request.headers.values())

        #sender_encrypted = self.request.get('se', '')
        #logging.debug('sender_encrypted ' + sender_encrypted)
        #sender = decode_cipher(sender_encrypted)
        #logging.debug('sender: ' + sender)

        sender = self.request.get('sender')
        subject = self.request.get('subject')
        token = self.request.get('token')
        tz_offset = int(self.request.get('tz_offset', 0))
        to = self.request.get('to')
        cc = self.request.get('cc')
        bcc = self.request.get('bcc')
        links = self.request.get('links')

        logging.info(sender)
        logging.info(subject)
        logging.info(token)
        logging.info(tz_offset)
        logging.info(to)
        logging.info(cc)
        logging.info(bcc)
        logging.info(links)

    def add(self):
        """
        create signal

        params:
        sync
        sender    TODO:(security?)
        subject
        to
        cc
        bcc
        links
        tz_offset

        """
        self.meta.change_view('json')
        self._enable_cors()

        if self.request.method != 'POST':
            self.response.status_code = 403
            return

# TODO: check user
#         user = users.get_current_user()
#         if not user:
#             self.context['data'] = dict(login_url=users.create_login_url())
#             self._enable_cors()
#             return

        # TODO: validate params
        sync = self.request.get('sync', False)
        token = self.request.get('token')
        version = self.request.get('version', '')

        sender = self.request.get('sender')
        subject = self.request.get('subject')

        outlook = self.request.get('outlook')
        debuginfo = self.request.get('debuginfo')

        track_state = self.request.get('track_state')
        track_state = False if track_state == "0" else True
        # reminder
        reminder_enabled = self.request.get('reminder_enabled')
        reminder_enabled = True if reminder_enabled == "1" else False
        reminder_timer_string = self.request.get('reminder_timer_string')
        reminder_if_no_reply = self.request.get('reminder_if_no_reply')
        reminder_if_no_reply = True if reminder_if_no_reply == "1" else False
        reminder_note = self.request.get('reminder_note')

        logging.info('track_state: %s' % track_state)
        logging.info('reminder_timer_string: %s' % reminder_timer_string)
        logging.info('reminder_if_no_reply: %s' % reminder_if_no_reply)
        logging.info('reminder_note: %s' % reminder_note)

        if self.current_user:
            logging.info('current_user: %s' % self.current_user)

        client = self.request.get("client")
        if outlook:
            logging.info("is_outlook")
            client = 'outlook'
        
        logging.info("sender %s" % sender)
        logging.info("version %s" % version)
        logging.info("token %s" % token)
        logging.info(subject)

        # client debuginfo
        try:
            logging.info('debuginfo:')
            for d in debuginfo.split(u'#_#'):
                if d:
                    logging.info(d)
        except:
            pass

        # TODO: this is temp solution
        try:
            tz_offset = int(self.request.get('tz_offset', 0))
            logging.info("tz_offset: %s" % tz_offset)
        except Exception as ex:
            logging.exception(ex)
            tz_offset = None
        try:
            timezoneinfo = self.request.get('timezoneinfo', "")
            if timezoneinfo:
                logging.info("timezoneinfo: %s" % timezoneinfo)
        except:
            pass

        if not is_email_valid(sender):
            logging.error('sender email not valid: %s' % sender)
            self.context['data'] = {'error': 'sender email not valid'}
            return

        # TODO: check legit for all users(gmail users), create alert in plugin first
        if not self._check_user_legit_and_create_or_update_user_last_seen_and_started(sender, tz_offset=tz_offset, sync=sync):
            logging.error('user_not_legit: %s' % sender)
            self.context['data'] = {'error': 'user_not_legit'}
            return

        # get email receivers
        # to, cc, bcc
        count = 0
        receivers = {}
        receiver_emails = []
        for k in Signal.receiver_keys():
            logging.info('receiver %s' % k)
            emails = self.request.get(k)
            if emails:
                logging.info(emails)

                receivers[k] = {}
                if '<' in emails or '>' in emails:  # because a User Name may contain ','
                    email_list = re.split(r'(?<=\>)\,', emails)
                else:
                    email_list = [emails]
                for email_string in email_list:  # for email_string in emails.split(','): some people have ',' in name
                    email_and_name = seperate_email_and_name(email_string)
                    if email_and_name:
                        logging.info(email_and_name)
                        receivers[k].update(email_and_name)
                        if email_and_name.keys():
                            receiver_emails.append(email_and_name.keys()[0])
                        count += 1
            else:
                receivers[k] = {}
        receivers.update(c=count)
        
        logging.info(receivers)
        logging.info(receiver_emails)
        
        try:
            links = self.request.get('links', '')
            if not links:
                links = '[]'
            links = json.loads(links)
        except Exception as ex:
            logging.exception(ex)

        # seperate the name and email

        if count < 1:
            logging.error("Receiver_count_less_than_1 %s" % token)
            self.context['data'] = {'error': 'receiver count less than 1'}
            return

        # create signal
        signal = Signal(token=token,
                        sender=sender,
                        subject=subject,
                        receivers=receivers,
                        receiver_emails=receiver_emails,
                        tz_offset=tz_offset,
                        client=client,
                        track_state=track_state
                        )

        if links and track_state:  # do not track links if not in track_state
            logging.info(links)
            self._save_links(links, signal, sync)

        try:
            signal.put() if sync else signal.put_async()
        except TransactionFailedError:
            signal.put_async()

        self._ensure_my_ass(sender, sync)
        self._update_statistic(signal, sync=sync)
        self.context['data'] = dict(signal=signal.to_dict(include=['token', 'sender', 'subject',
                                                                   'receivers', 'access_count', 'receiver_emails',
                                                                   'country', 'city', 'device']))
        # add_reminder
        if reminder_enabled:
            Reminder.add_reminder_to_taskqueue(reminder_timer_string, reminder_if_no_reply, reminder_note, sender, token)
        
        #asign gmail id to signal
        if client == "gmail":
            tos = receivers["to"].keys() if receivers.get("to") else []
            ccs = receivers["cc"].keys() if receivers.get("cc") else []
            bccs = receivers["bcc"].keys() if receivers.get("bcc") else []
            naughty_gmail_api_calm_down_and_will_give_me_real_thread_id_in_seconds = 60
            taskqueue.add(
                url='/assign_gmail_id_to_signal',
                method='GET',
                countdown=naughty_gmail_api_calm_down_and_will_give_me_real_thread_id_in_seconds,
                params={'sender': sender,
                        'signal_id': signal.key.id(),
                        'tos': json.dumps(tos),
                        'ccs': json.dumps(ccs),
                        'bccs': json.dumps(bccs)
                        }
            )
        return
#         self.response.headers.add_header('Access-Control-Allow-Origin', '*.google.com')
        
    @route_with('/assign_gmail_id_to_signal')
    def assign_gmail_id_to_signal(self):
        self.meta.change_view('json')
        sender = self.request.get('sender')
        logging.info("reminder sender: %s" % sender)
        try:
            signal_id = int(self.request.get('signal_id'))
        except:
            logging.exception("signal_id")
            return
        tos = json.loads(self.request.get('tos'))
        ccs = json.loads(self.request.get('ccs'))
        bccs = json.loads(self.request.get('bccs'))
        user_info = UserInfo.find_by_properties(email=sender)
        user_google_id = user_info.google_id
        logging.info('user_google_id %s' % user_google_id)
            
        if not user_google_id:
            logging.warning("UserInfoNoGoogleID %s" % sender)
            return
        if not (user_info.google_id and user_info.refresh_token):
            return
            
        signal = Signal.get_by_id(signal_id)
        if not signal:
            logging.error('Signal not found')
            return
        logging.info(signal.token)
        try:
            client = GoogleMessageClient(user_info=user_info)
            result = client.search_threads(limit=3)
            logging.info(result)
            result = client.search_threads(signal.subject, tos, ccs, bccs, limit=1)
            logging.info("ThreadsSearchResult:")
            logging.info(result)
            if result and result["threads"]:
                thread_id = result["threads"][0]["id"]
                logging.info("thread_id %s" % thread_id)
                signal.gmail_id = thread_id
                signal.put()
        except Exception as ex:
            logging.exception(ex)
        self.context['data'] = {}

    def _check_user_legit_and_create_or_update_user_last_seen_and_started(self, sender, tz_offset=0, sync=True):
        """
        check if the user is legit
        if user is legit return user
        else return None
        """
        # TODO: remove this testing
        if tz_offset == 0:
            logging.warning('tz_offset: %s' % tz_offset)

        user = UserInfo.find_by_properties(email=sender)
        if not user:
            logging.warning('_check_user_legit_user_not_found')
            # return False

        # TODO: UserInfo creation process should be in auths.py or user_info.py
        update_user = False
        utcnow = datetime.utcnow()
        if not user:
            user = UserInfo.create_user(
                email=sender,
                orgs=['daily', 'weekly', 'activity'],
                last_seen=utcnow,
                domain=sender.split('@')[1].lower(),
                tz_offset=tz_offset,
                started=utcnow,
                created=utcnow,
                save=False
            )
            update_user = True
        else:
            if not user.started:
                user.started = utcnow
                update_user = True

            if not user.last_seen \
                    or utcnow - user.last_seen > timedelta(hours=12):
                # update not less than 12 hours
                user.last_seen = utcnow
                update_user = True

            if user.tz_offset != tz_offset:
                user.tz_offset = tz_offset
                update_user = True

        if update_user:
            user.put() if sync else user.put_async()

        # TODO: enable it
#         if is_user_legit(user):
#             return user
#         else:
#             return False
        return user

    def _save_links(self, links, signal, sync):
        """
        {url:url,
        urlDecoded:urlDecoded,
        urlHash:urlHash,
        plain:plain}

        TODO: link url and urlHash could be the same, improve this
        """
        links_to_save = []
        for l in links:
            link = Link(
                token=signal.token,
                sender=signal.sender,
                subject=signal.subject,
                receiver_emails=signal.receiver_emails,
                url_id=l['urlHash'],
                url=l['urlDecoded']
            )
            links_to_save.append(link)

        if sync:
            ndb.put_multi(links_to_save)
        else:
            ndb.put_multi_async(links_to_save)

    def _update_statistic(self, signal, sync=False):
        statistic = Statistic.find_by_properties(email=signal.sender)
        if statistic:
            statistic.monthly_signal_count += 1
        else:
            statistic = Statistic.create(email=signal.sender, monthly_signal_count=1)

    @route_with('/resource/signals')
    def get_signals(self):
        self.meta.change_view('json')
        self._enable_cors()

        sender = self.request.get('sender')
        logging.info('sender %s' % sender)
        if not sender:
            logging.error('no sender')
            return

        #signals = Signal.query(Signal.sender == sender).order(-Signal.created).fetch(100)
        signals = Signal.query(Signal.sender==sender, Signal.track_state.IN([True, None])).order(-Signal.created).fetch(100)
        self.context['data'] = dict(data=[s.to_dict(
            include=['token', 'sender', 'subject', 'access_count',
                     'receivers', 'receiver_emails',
                     'country', 'city', 'device',
                     'created', 'modified']) for s in signals])

    @route_with('/s/')
    def reply_robot(self):
        """
        reply to:
        1. Microsoft Office Protocol Discovery
        Microsoft has a kb article that covers Protocol Discovery in fine detail.
        Essentially, Office is trying to determine if your server supports WebDAV (or something like it)
        so that changes the user makes to the Office document can be pushed back directly to the server.
        """
        self.meta.change_view('json')

    @route_with('/s/s.gif')
    def get_signal_image(self):
        """
        1.find signal by token
        2.record access
        3.increase access_count
        4.if identify user, generate relation, user cookie

        defer:
        1. notify sender
        2.
        return: generated image

        <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7">

        """

        token = self.request.get('t')
        logging.info('token %s' % token)
        sync = self.request.get('sync')

        signal_is_rocessing = memcache.get('signal::%s' % token)  # @UndefinedVariable
        if signal_is_rocessing is not None:
            logging.warning('access_too_frequently1')
            self.create_response_image()
            return self.response
        else:
            memcache.add('signal::%s' % token, True, 1)  # @UndefinedVariable

        signal = Signal.find_by_properties(token=token)
        if not signal:
            # TODO: return what? image?
            logging.warning('no signal')
            self.create_response_image()
            return self.response

        if datetime.utcnow() - signal.modified < timedelta(seconds=5) \
                and signal.modified - signal.created > timedelta(seconds=3):
            logging.warning('access_too_frequently2')
            self.create_response_image()
            return self.response

        logging.info('headers')
        logging.info(self.request.headers.keys())
        logging.info(self.request.headers.values())
        logging.info('User-Agent: %s' % self.request.headers.get('User-Agent'))
        logging.info('remote_addr %s' % self.request.remote_addr)

        # how many potential receivers

        accessor, ass = self._recognize_user(signal, sync)
        logging.info('accessor: %s, ass:%s' % (accessor, ass))

        pickle.dumps(sync)
        pickle.dumps(ass)
        pickle.dumps(accessor)
        pickle.dumps(signal)
        # prevent self access
        if not (accessor and signal.sender in accessor.keys()):
            signal.access_count += 1
            # save signal first, to generate signal.key for access as parent
            signal.put()
            # no deferred here, a handler function can't be deferred
            access = self._create_access_record(signal, accessor, ass, sync=sync)
            signal.country = access.country
            signal.city = access.city
            signal.device = access.device
            signal.put()
        else:
            logging.info('self_access')

        memcache.set('signal::%s' % token, None)  # @UndefinedVariable

        self.create_response_image()
        return self.response

    def create_response_image(self):
        self.response.content_type = 'image/gif'
        self.response.headers['cache-control'] = 'private, max-age=0, no-cache'
        self.response.text = u'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'

    def _create_access_record(self, signal, accessor, ass, sync=False):
        """
        """
        logging.info('_create_access_record')
        # TODO: should it be moved to taskqueue

        source = self._get_source_info()
        access = Access(parent=signal.key,
                        token=signal.token,
                        sender=signal.sender,
                        accessor=accessor.keys()[0] if accessor else None,
                        accessor_name=accessor[accessor.keys()[0]] if accessor else None,
                        ass=ass if ass else None,
                        ip=self.request.remote_addr,
                        user_agent=self.request.headers.get('User-Agent', None),
                        proxy=source.proxy if source else None,
                        device=source.device if source else None,
                        country=source.country if source else None,
                        city=source.city if source else None,
                        tz_offset=source.tz_offset if source else None,
                        kind='open'
                        )
        # TODO: async later, now use sync for the email
        #access.put() if sync else access.put_async()
        try:
            access.put()
            self._notify_sender(signal, access, sync=sync)
        except TransactionFailedError:
            access.put_async()
            # TODO: customize _notify_sender if put failed

        return access

    @route_with('/settings/notification/update')
    def update_notification(self):
        code = self.request.get('c', '')
        notification_setting = self.request.get('ns', '')
        logging.info('code %s' % code)
        self.context['code'] = code

        token = Signal.decode_signal_token(code)
        logging.info('token %s' % token)
        if not token:
            logging.warning('no token, return')
            self.context['success'] = False
            return

        signal = Signal.find_by_properties(token=token)
        if not signal:
            logging.info('no signal of this token: %s' % token)
            self.context['success'] = False
            return

        if notification_setting in Signal.notification_settings():
            signal.notification_setting = notification_setting
            signal.put()
            logging.info('notification_setting of Signal:%s change to:%s' % (token, notification_setting))
            self.context['success'] = True
        else:
            logging.warning('notification_setting %s not in %s' % (notification_setting, Signal.notification_settings()))
            self.context['success'] = False


