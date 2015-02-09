# -*- coding: utf-8 -*-
'''
Created on 2015/1/15

@author: sushih-wen
'''
import json
import logging
import base64
from uuid import uuid4
from google.appengine.ext import testbed
from ferrisnose import AppEngineTest, AppEngineWebTest, FerrisAppTest
from app.models.signal import Signal
from app.models.access import Access
from app.models.link import Link
from app.models.user_info import UserInfo
from app.controllers.links import Links
from app.controllers.signals import Signals


class TestSignal(AppEngineTest):

    """
    test model
    """

    def testCreate(self):
        self.loginUser('user1@example.com')
        signal = Signal()


class TestSignalController(AppEngineWebTest):

    """
    test
    """

    def setUp(self):
        AppEngineWebTest.setUp(self)
        self.add_controller(Links)
        self.add_controller(Signals)
        self.mail_stub = self.testbed.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def createUser(self, sender='sender@asdf.com', orgs=['test'], role=1, tz_offset=9):
        user = UserInfo(
            email=sender,
            orgs=orgs,
            role=role,
            tz_offset=tz_offset
        )
        user.put()

    #TODO: merge into test_signal
    def requestCreateSignal(self, sender='sender@asdf.com', subject='Mail to Su', to='', cc='', bcc=''):
        r = self.testapp.post('/signals/add?sync=1',
                              {'sender': sender,
                               'subject': subject,
                               'token': str(uuid4()).replace('-', '')[:12],
                               'to': to,
                               'cc': cc,
                               'bcc': bcc},
                              xhr=True)
        return r

    #TODO: merge into test_signal
    def createSignal(self, sender='sender@asdf.com', subject='Mail to Su', to='蘇 <to1@asdf.com>'):

        r = self.requestCreateSignal(sender, subject, to=to)
        logging.debug(r.status)
        logging.debug(r.body)
        #signal = json.loads(r.body)['signal']
        signal = Signal.find_by_properties(token=json.loads(r.body)['signal']['token'])
        return signal
        
    def createLink(self, sender='sender@asdf.com', subject='Hello', receiver_emails= ['to1@asdf.com', 'to2@asdf.com'], token='asdf145134',
                   url='http://www.google.com', url_id='test123', 
                   access_count=1,
                   country = 'Japan', city='Tokyo', device='iPhone'):

        link = Link(
                    sender=sender,
                    subject=subject,
                    token=token,
                    receiver_emails=receiver_emails,
                    url=url,
                    url_id=url_id,
                    country=country,
                    city=city,
                    device=device,
                    access_count=access_count
                    )
        link.put()
        return link
        
    def testGetLinks(self):
        sender = 'sender@asdf.com'
        receiver_emails=['to1@asdf.com', 'to2@asdf.com']
        country='Japan'
        city='Tokyo'
        device='iPhone'
        subject='Hello'
        self.createLink(sender=sender, 
                        access_count=0, 
                        subject=subject,
                        receiver_emails=receiver_emails,
                        country=country,
                        city=city,
                        device=device)
        self.createLink(sender=sender, access_count=1)
        r = self.testapp.get('/resource/links?sender=%s&accssed=1' % sender)
        self.assertEqual(r.status_code, 200)
        result = json.loads(r.body)
        logging.info(result)
        links = result['data']
        self.assertEqual(len(links), 2)
        self.assertEqual(links[0]['receiver_emails'], receiver_emails)
        self.assertEqual(links[0]['country'], country)
        self.assertEqual(links[0]['city'], city)
        self.assertEqual(links[0]['device'], device)
        self.assertEqual(links[0]['subject'], subject)
    
    def testAccessLinks(self):
        sender = 'sender@asdf.com'
        url_id = 'hash123'
        signal = self.createSignal(sender=sender)
        self.createLink(sender=sender, access_count=0, token=signal.token, url_id=url_id)
        r = self.testapp.get('/l?t=%s&h=%s' % (signal.token, url_id), extra_environ={'REMOTE_ADDR': '168.95.1.1'})
        self.assertEqual(r.status_code, 302)
        link = Link.find_by_properties(sender=sender)
        self.assertEqual(link.access_count, 1)
