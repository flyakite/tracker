# -*- coding: utf-8 -*-
'''
Created on 2014/10/8

@author: sushih-wen
'''
import json
import logging
from datetime import datetime, timedelta
from uuid import uuid4
from google.appengine.ext import testbed
from ferrisnose import AppEngineTest, AppEngineWebTest, FerrisAppTest
from app.models.signal import Signal
from app.models.access import Access
from app.models.user_info import UserInfo
from app.models.channel_client import ChannelClient
from app.controllers.accesses import Accesses, AccessNotification
from app.controllers.admins import Admins


class TestAdminOperation(AppEngineWebTest):

    """
    test
    """

    def setUp(self):
        AppEngineWebTest.setUp(self)
        self.add_controller(Admins)
        self.mail_stub = self.testbed.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def testUserList(self):

        try:
            r = self.testapp.get('/admin/user_list')
            logging.debug(r)
        except Exception as e:
            logging.debug(e)

        self.loginUser('admin@asdf.com', admin=True)

        user = 'user1@asdf.com'
        ChannelClient(owner=user,
                      client_id='7d8e683fce3040e6b36a2fjeiksov543'
                      ).put()

        UserInfo(email=user,
                 orgs=['test']).put()

        r = self.testapp.get('/admin/user_list')
        logging.debug(r)
        assert r.status_code == 200
        r = self.testapp.get('/admin/user_list?org=test')
        logging.debug(r)
        assert r.status_code == 200
        r = self.testapp.get('/admin/user_list?connected=1')
        logging.debug(r)
        assert r.status_code == 200

    def testFixUserStarted(self):
        for email in ['user1@asdf.com', 'user2@asdf.com']:
            UserInfo(email=email,
                     orgs=['test'],
                     last_seen=datetime.utcnow()
                     ).put()
        r = self.testapp.get('/admin/fix_user_started', {'emails': 'user1@asdf.com,user2@asdf.com'})
        assert r.status_code == 200
        user = UserInfo.find_by_properties(email='user2@asdf.com')
        logging.info(user)
        assert user.started

    def testLegitUser(self):
        for email in ['user1@asdf.com', 'user2@asdf.com']:
            UserInfo(email=email,
                     orgs=['test'],
                     last_seen=datetime.utcnow()
                     ).put()
        r = self.testapp.get('/admin/legit_user', {'emails': 'user1@asdf.com,user2@asdf.com,user3@asdf.com',
                                                   'orgs': 'a,b'})
        assert r.status_code == 200
        user = UserInfo.find_by_properties(email='user2@asdf.com')
        logging.info(user)
        self.assertEqual(user.role, 1)
        self.assertEqual(user.orgs, ['a', 'b'])
        user = UserInfo.find_by_properties(email='user3@asdf.com')
        logging.info(user)
        self.assertEqual(user.role, 1)
        self.assertEqual(user.orgs, ['a', 'b'])
        self.assertEqual(user.domain, 'asdf.com')
