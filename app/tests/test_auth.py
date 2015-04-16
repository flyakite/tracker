'''
Created on 2014/11/28

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
from app.models.domain import Domain
from app.models.channel_client import ChannelClient
from app.models.device_client import DeviceClient
from app.controllers.accesses import Accesses, AccessNotification
from app.controllers.auths import Auths
from test_base import TestBase


class TestAuth(TestBase):

    """
    test
    """

    def setUp(self):
        TestBase.setUp(self)
        self.add_controller(Auths)

    def testLogin(self):
        r = self.testapp.get('/auth/login')
        self.assertIn(r.status_code, [301, 302])

    def testAuthUser(self):
        r = self.testapp.get('/auth/user')
        assert r.status_code == 200
        j = json.loads(r.body)
        logging.info(j)
        self.assertEqual(j['error'], True)
        # TODO: test login session user

    def testAuthLegit(self):

        r = self.testapp.get('/auth/legit')
        assert r.status_code == 200

        r = self.testapp.get('/auth/legit', {'email': 'user'})
        assert json.loads(r.body)['result'] == 0

        Domain(
            domain='asdf.com',
            position=1
        ).put()

        r = self.testapp.get('/auth/legit', {'email': 'user@asdf.com'})
        logging.info(dir(r))
        assert json.loads(r.body)['result'] == 1

        UserInfo(
            email='user1@qwer.com',
            role=0
        ).put()
        UserInfo(
            email='user2@qwer.com',
            role=1
        ).put()

        r = self.testapp.get('/auth/legit', {'email': 'user1@qwer.com'})
        logging.info(dir(r))
        assert json.loads(r.body)['result'] == 0

        r = self.testapp.get('/auth/legit', {'email': 'user2@qwer.com'})
        logging.info(dir(r))
        assert json.loads(r.body)['result'] == 1

    def testAuthActivateAccount(self):
        r = self.testapp.post('/auth/activate_account', {'email': 'asdf@asdf.com',
                                                         'client_id': str(uuid4()),
                                                         'client_name': 'my_pc'})
        assert r.status_code == 200
        assert json.loads(r.body)['success']

        r = self.testapp.post('/auth/activate_account', {'email': 'asdf@asdf.com'})
        assert r.status_code == 200
        assert json.loads(r.body)['success'] == False

    def testAuthVerifyClient(self):
        r = self.testapp.post('/auth/verify_client', {'client_id': str(uuid4()),
                                                      'client_name': 'my_pc'})
        assert r.status_code == 200
        assert json.loads(r.body)['success'] == False

        client_id = str(uuid4())
        email = 'asdf@asdf.com'
        DeviceClient(owner=email, client_id=client_id).put()

        r = self.testapp.post('/auth/verify_client', {'client_id': client_id,
                                                      'client_name': 'my_pc'})
        assert r.status_code == 200
        assert json.loads(r.body)['success']
        self.assertEqual(json.loads(r.body)['data'], email, 'first email')

        email2 = 'asdf@asdf.com'
        DeviceClient(owner=email2, client_id=client_id).put()

        r = self.testapp.post('/auth/verify_client', {'client_id': client_id,
                                                      'client_name': 'my_pc'})
        assert r.status_code == 200
        assert json.loads(r.body)['success']
        self.assertEqual(json.loads(r.body)['data'], email2, 'second email')
