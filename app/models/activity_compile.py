'''
Created on 2014/10/5

@author: sushih-wen
'''
import logging
import base64
import cPickle as pickle
from Crypto.Cipher import AES
from ferris import BasicModel
from google.appengine.ext import ndb
from google.appengine.api import users


AES_KEY = 'asdfqwerzxcv12345678901234567890'  # must be a multiple of 16 in length, deprecated


class ActivityCompile(BasicModel):
    senders = ndb.StringProperty(repeated=True)
    start = ndb.DateTimeProperty()
    end = ndb.DateTimeProperty()
#     sort = ndb.StringProperty()
#
#
#     @staticmethod
#     def sorts(self):
#         """
#         o: open
#         """
#         return ['o']

    @staticmethod
    def encrypt_activity_compile_to_code(activity_compile):
        try:
            code = pickle.dumps(activity_compile)
            # AES
            obj = AES.new(AES_KEY, AES.MODE_ECB)
            # Input strings must be a multiple of 16 in length
            code = code + '=' * (16 - len(code) % 16)
            code = obj.encrypt(code)
            code = base64.urlsafe_b64encode(code)
            return code
        except Exception as e:
            logging.error('encrypt_activity_compile_to_code error')
            logging.error(e)
            return ''

    @staticmethod
    def decrypt_code_to_activity_compile(code):
        code = str(code)
        try:
            code = base64.urlsafe_b64decode(code)
            obj = AES.new(AES_KEY, AES.MODE_ECB)
            code = obj.decrypt(code)
            code = code.rstrip('=')
            activity_compile = pickle.loads(code)
            return activity_compile
        except Exception as e:
            logging.error('decrypt_code_to_activity_compile error')
            logging.error(e)
            return None
