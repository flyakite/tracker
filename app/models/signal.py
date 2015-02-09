import logging
import base64
import zlib
from ferris import BasicModel
from google.appengine.ext import ndb

_CRC_START = 91347536


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
    country = ndb.TextProperty() #last access
    city = ndb.TextProperty() #last access
    device = ndb.TextProperty() #last access
    tz_offset = ndb.IntegerProperty(default=0)
    notification_setting = ndb.StringProperty()
    notify_triggered = ndb.DateTimeProperty()
    client = ndb.StringProperty()  # None for Gmail, 'outlook'

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
