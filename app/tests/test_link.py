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
from test_base import TestBase


class TestSignal(AppEngineTest):

    """
    test model
    """

    def testCreate(self):
        self.loginUser('user1@example.com')
        signal = Signal()


class TestSignalController(TestBase):

    """
    test
    """

    def setUp(self):
        AppEngineWebTest.setUp(self)
        self.add_controller(Links)
        self.add_controller(Signals)
        self.mail_stub = self.testbed.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def create_link(self, sender='sender@asdf.com', subject='Hello', receiver_emails=['to1@asdf.com', 'to2@asdf.com'], token='asdf145134',
                   url='http://www.google.com', url_id='test123',
                   access_count=1,
                   country='Japan', city='Tokyo', device='iPhone',
                   is_accessed=False):

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
            access_count=access_count,
            is_accessed=is_accessed
        )
        link.put()
        return link

    def test_get_links(self):
        sender = 'sender@asdf.com'
        receiver_emails = ['to1@asdf.com', 'to2@asdf.com']
        country = 'Japan'
        city = 'Tokyo'
        device = 'iPhone'
        subject = 'Hello'
        self.create_link(sender=sender,
                        access_count=0,
                        subject=subject,
                        receiver_emails=receiver_emails,
                        country=country,
                        city=city,
                        device=device,
                        is_accessed=True)
        self.create_link(sender=sender, access_count=1, is_accessed=True)
        r = self.testapp.get('/resource/links?sender=%s&accessed=1' % sender)
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

    def test_access_links(self):
        sender = 'sender@asdf.com'
        url_id = 'hash123'
        signal = self.create_signal(sender=sender)
        self.create_link(sender=sender, access_count=0, token=signal.token, url_id=url_id)
        r = self.testapp.get('/l?t=%s&h=%s' % (signal.token, url_id), extra_environ={'REMOTE_ADDR': '168.95.1.1'})
        self.assertEqual(r.status_code, 302)
        link = Link.find_by_properties(sender=sender)
        self.assertEqual(link.access_count, 1)
