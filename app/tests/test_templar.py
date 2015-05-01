# -*- coding: utf-8 -*-
'''
Created on 2015/4/26

@author: sushih-wen
'''
import json
import logging
import base64
from uuid import uuid4
from google.appengine.ext import testbed
from ferrisnose import AppEngineTest, AppEngineWebTest, FerrisAppTest
from app.models.templar import Templar
from app.controllers.templars import Templars
from test_base import TestBase



class TestTemplarTestCase(TestBase):

    def setUp(self):
        AppEngineWebTest.setUp(self)
        self.add_controller(Templars)
        self.mail_stub = self.testbed.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def create_templar(self, tid=uuid4().hex, subject='subject', body='body', owner='user1@asdf.com', 
                       used_times=0, replied_times=0, opened_times=0, is_active=True):
        t = Templar(
            tid = tid,
            subject = subject,
            body = body,
            owner = owner,
            used_times = used_times,
            replied_times = replied_times,
            opened_times = opened_times,
            is_active = is_active,
        )
        t.put()
        return t
        
    def test_get_templars(self):
        owner = 'user1@asdf.com'
        t = self.create_templar()
        r = self.testapp.get('/resource/templars', {'access_token': 'test', 'owner':owner})
        self.assertEqual(r.status_code, 200)
        jdata =json.loads(r.body)
        logging.info(jdata['data'])
        self.assertEqual(len(jdata['data']), 1)
        self.assertEqual(jdata['data'][0]['owner'], owner)
        self.assertEqual(jdata['data'][0]['tid'], t.tid)

    def test_create_templar(self):
        owner = 'user1@asdf.com'
        r = self.testapp.post('/resource/templar', {'action': 'create',
                                                    'access_token': 'test', 'owner':owner, 'subject':'subject', 'body':'body'})
        self.assertEqual(r.status_code, 200)
        jdata =json.loads(r.body)
        logging.info(jdata)
        self.assertEqual(jdata['owner'], owner)
        self.assertTrue(jdata['tid'])

    def test_delete_templar(self):
        owner = 'user1@asdf.com'
        t = self.create_templar()
        r = self.testapp.post('/resource/templar', {'action': 'delete',
                                                    'access_token': 'test', 'owner':owner, 'tid':t.tid})
        self.assertEqual(r.status_code, 200)
        jdata =json.loads(r.body)
        logging.info(jdata)
        self.assertEqual(jdata['success'], 1)
        
        
        