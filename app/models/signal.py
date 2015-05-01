import logging
import base64
import zlib
from datetime import timedelta
from libs.dateutil import parser as date_parser
from libs.dateutil import tz
from ferris import BasicModel
from google.appengine.ext import ndb
from app.libs.google_client import GoogleMessageClient
from app.models.user_info import UserInfo
import templar

_CRC_START = 91347536
WE_HAVE_NO_EMAIL_AUTHORITY_MESSAGE = "We have no authority to check who replied your email."

class Signal(BasicModel):

    """

    receivers:
    {
        "to":{"abc@bcd.com":"A BC",
            "ddd@bcd.com":"D DD"},
        "cc":null,
        "bcc":null,
        "c":2
    }


    """

    token = ndb.StringProperty(required=True)
    sender = ndb.StringProperty(required=True)
    subject = ndb.TextProperty()
    access_count = ndb.IntegerProperty(default=0)
    receivers = ndb.JsonProperty()
    receiver_emails = ndb.StringProperty(repeated=True)
    country = ndb.TextProperty()  # last access
    city = ndb.TextProperty()  # last access
    device = ndb.TextProperty()  # last access
    tz_offset = ndb.IntegerProperty(default=0)
    notification_setting = ndb.StringProperty()
    notify_triggered = ndb.DateTimeProperty()
    client = ndb.StringProperty()  # None for Gmail, 'outlook'
    gmail_id = ndb.StringProperty()
    thread_id = ndb.StringProperty()
    track_state = ndb.BooleanProperty()
    replied = ndb.DateTimeProperty()
    first_accessed = ndb.DateTimeProperty()
    templar_id = ndb.StringProperty()
    

    @staticmethod
    def receiver_keys():
        return ['to', 'cc', 'bcc']

    def to_dict_output(self, include=['token', 'sender', 'subject', 'access_count'], exclude=[]):
        return self.to_dict(include=include, exclude=exclude)

    @staticmethod
    def notification_settings():
        """
        e: email only
        d: desktop notification only
        disable: no notification
        None: both notification, default
        """
        return ['e', 'd', 'disable', None]

    @staticmethod
    def decode_signal_token(code):
        code = str(code)
        try:
            token, crc = code.split('.')
            token = base64.urlsafe_b64decode(token)
            assert zlib.crc32(token, _CRC_START) == int(crc)
            return token
        except Exception as e:
            logging.warning('decode_signal_token failed')
            logging.warning(e)
            return None

    @staticmethod
    def encode_signal_token(token):
        return "%s.%s" % (base64.urlsafe_b64encode(token), zlib.crc32(token, _CRC_START))

    def created_consider_tz_offset(self):
        return self.created + timedelta(hours=self.tz_offset)


    def has_reply(self, update_signal=False):
        if self.replied:
            return True
            
        user_info = UserInfo.find_by_properties(email=self.sender)
        user_google_id = user_info.google_id
        refresh_token = user_info.refresh_token
        if refresh_token and user_google_id:
            try:
                client = GoogleMessageClient(user_info=user_info)
                thread_id = client.get_message_thread_id(self.gmail_id)
                logging.info(thread_id)
                threads = client.get_threads(thread_id)
                messages = client.get_messages_from_threads(threads)
                logging.info(messages)
                if self.receivers.get('to'):
                    emails = self.receivers['to'].keys()
                else:
                    emails = self.receiver_emails[:1]
                logging.info('check replies from %s' % emails)
                reply = reply_from_emails_after_message_id(emails, self.gmail_id, messages)
                logging.info(reply)
                if reply:
                    logging.info('has reply')
                    if update_signal:
                        self.update_signal_replied_from_message(reply)
                    return True
                else:
                    logging.info('no reply')
                    return False
            except Exception as ex:
                logging.exception(ex)
                return False
        else:
            logging.error(
                'trigger_reminder missing parms Error sender: %s google_id: %s refresh_token:%s' %
                (self.sender, refresh_token, user_google_id))
            self.context['message'] = WE_HAVE_NO_EMAIL_AUTHORITY_MESSAGE
            return False
            
    def update_signal_replied_from_message(self, message):
        payload = message['payload']
        headers = payload['headers']
        for h in headers:
            if h['name'].lower() == "date":
                self.replied = date_parser.parse(h['value']).astimezone(tz.tzutc()).replace(tzinfo=None)
                #make up access_count, because there is a reply, there must be an access
                if not self.first_accessed:
                    self.first_accessed = self.replied
                if self.access_count == 0:
                    self.access_count = 1
                    if self.templar_id:
                        templar.Templar.update_statistics(self.templar_id, replied_times_delta=1, opened_times_delta=1)
                else:
                    if self.templar_id:
                        templar.Templar.update_statistics(self.templar_id, replied_times_delta=1)
                self.put()
                return
            
def reply_from_emails_after_message_id(emails, message_id, messages):
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
    logging.info("email %s" % emails)
    
    history_id = 0
    for m in messages:
        if m['id'] == message_id:
            try:
                history_id = int(m.get('historyId', 0))
            except:
                logging.exception("history_id")
                history_id = 0
            break
            
    for m in messages:
        try:
            hid = int(m['historyId'])
            if hid < history_id:
                #this history id of the replies must be greater or equal to the sent email
                continue
            payload = m['payload']
            headers = payload['headers']
            for h in headers:
                #logging.info(h)
                for email in emails:
                    if h['name'].lower() == "from" and "<%s>" % email in h['value']:
                        logging.info(h['value'])
                        return m
        except:
            logging.exception("replies_from_email_after_message_id")
            continue
            
    return None