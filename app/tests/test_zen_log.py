'''
Created on 2014/12/4

@author: sushih-wen
'''
import json
import logging
from datetime import datetime, timedelta
from uuid import uuid4
from google.appengine.ext import testbed
from ferrisnose import AppEngineTest, AppEngineWebTest, FerrisAppTest
from app.controllers.zen_log import ZenLog


class TestAuth(AppEngineWebTest):

    """
    test
    """

    def setUp(self):
        AppEngineWebTest.setUp(self)
        self.add_controller(ZenLog)
        self.mail_stub = self.testbed.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def testLogin(self):
        r = self.testapp.get('/zenlog')
        self.assertEqual(r.status_code, 200)
