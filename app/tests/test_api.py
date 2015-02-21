'''
Created on 2014/12/27

@author: sushih-wen
'''
import json
import logging
from datetime import datetime, timedelta
from uuid import uuid4
from google.appengine.ext import testbed
from ferrisnose import AppEngineTest, AppEngineWebTest, FerrisAppTest
from app.models.api_key import ApiKey
from app.models.setting import Setting
from app.controllers.apis import Apis
from app.controllers.auths import encode_token, decode_token

class TestAuth(AppEngineWebTest):

    """
    test
    """

    def setUp(self):
        AppEngineWebTest.setUp(self)
        self.add_controller(Apis)
        self.mail_stub = self.testbed.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

#     def test_create_secret(self):
#         key = ApiKey.create_key()
#         secret = ApiKey.create_secret(key)
#         self.assertTrue(ApiKey.verify_secret(key, secret))
# 
#     def test_create_token(self):
#         key = ApiKey.create_key()
#         secret = ApiKey.create_secret(key)
#         token = ApiKey.create_token(key, secret)
#         self.assertTrue(ApiKey.verify_token(key, token))

    def test_settings(self):
        sender='sender@asdf.com'
        access_token = encode_token({'email':sender})
        r = self.testapp.get('/settings',
                              {
                               'access_token': access_token,
                               'email': sender,
                               'is_notify_by_email': 1,
                               'is_notify_by_desktop': ''
                              },
                              xhr=True)
        self.assertEqual(r.status_code, 200)
        
        r = self.testapp.post('/settings',
                              {
                               'access_token': access_token,
                               'email': sender,
                               'is_notify_by_email': 1,
                               'is_notify_by_desktop': ''
                              },
                              xhr=True)
        self.assertEqual(r.status_code, 200)
        s = Setting.find_by_properties(email=sender)
        self.assertEqual(s.is_notify_by_email, True)
        self.assertEqual(s.is_notify_by_desktop, False)
        
        r = self.testapp.get('/settings',
                              {
                               'access_token': access_token,
                               'email': sender,
                               'is_notify_by_email': 1,
                               'is_notify_by_desktop': ''
                              },
                              xhr=True)
        self.assertEqual(r.status_code, 200)