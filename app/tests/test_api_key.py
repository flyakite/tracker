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
from app.controllers.apis import Apis


class TestAuth(AppEngineWebTest):

    """
    test
    """

    def setUp(self):
        AppEngineWebTest.setUp(self)
        self.add_controller(Apis)
        self.mail_stub = self.testbed.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def test_create_secret(self):
        key = ApiKey.create_key()
        secret = ApiKey.create_secret(key)
        self.assertTrue(ApiKey.verify_secret(key, secret))

    def test_create_token(self):
        key = ApiKey.create_key()
        secret = ApiKey.create_secret(key)
        token = ApiKey.create_token(key, secret)
        self.assertTrue(ApiKey.verify_token(key, token))
