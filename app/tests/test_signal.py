# -*- coding: utf-8 -*-
import json
import logging
import base64
from uuid import uuid4
from google.appengine.ext import testbed
from ferrisnose import AppEngineTest, AppEngineWebTest, FerrisAppTest
from app.models.signal import Signal
from app.models.access import Access
from app.models.templar import Templar
from app.models.user_info import UserInfo
from app.controllers.signals import Signals
from app.controllers.signals import seperate_email_and_name
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
        self.add_controller(Signals)
        self.mail_stub = self.testbed.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

# TODO: no authentication now
#     def testLogin(self):
#         r = self.testapp.post('/signals/add',
#                               xhr=True)
#         self.assertTrue('login_url' in r)

#     def create_user(self, sender='sender@asdf.com', orgs=['test'], role=1, tz_offset=9):
#         user = UserInfo(
#             email=sender,
#             orgs=orgs,
#             role=role,
#             tz_offset=tz_offset
#         )
#         user.put()

    def testSeperateEmailAndName(self):
        self.assertEqual(seperate_email_and_name('asdf@asdf.com'), {'asdf@asdf.com': ''})
        self.assertEqual(seperate_email_and_name('Nice <asdf@asdf.com>'), {'asdf@asdf.com': 'Nice'})
        self.assertEqual(seperate_email_and_name('Nice <asdf!asdf.com>'), None)

    def test_request_create_signal(self):
        self.loginUser('sender@asdf.com')
        sender = 'sender@asdf.com'
        subject = 'Mail to Su'
        to = '蘇 <to1@asdf.com>, K J <to2@asdf.com>'
        self.create_user(sender)
        r = self.request_create_signal(sender, subject, to)
        signal = Signal.find_by_properties(sender=sender)

        self.assertEqual(signal.sender, sender)
        self.assertEqual(r.content_type, 'application/json')
        body = json.loads(r.body)['signal']
        self.assertEqual(body['token'], signal.token)
        self.assertEqual(body['sender'], sender)
        self.assertEqual(body['subject'], subject)
        self.assertEqual(body['receivers']['to']['to1@asdf.com'], u'蘇')
        self.assertEqual(body['receivers']['to']['to2@asdf.com'], u'K J')
        self.assertEqual(body['receivers']['cc'], {})
        self.assertEqual(body['receivers']['bcc'], {})
        self.assertEqual(body['receiver_emails'], ['to1@asdf.com', 'to2@asdf.com'])

#     def testGetIPInfo(self):
#         s = Signals()
#         ipinfo = s.get_ip_info(ipaddress='168.95.1.1')
#         logging.info(ipinfo)
#         assert ipinfo.country == 'TW'


    def test_request_create_signal_gmail(self):
        self.loginUser('sender@asdf.com')
        sender = 'sender@asdf.com'
        subject = 'Mail to Su'
        to = '蘇 <to1@asdf.com>, K J <to2@asdf.com>'
        self.create_user(sender)
        r = self.request_create_signal(sender, subject, to)
        signal = Signal.find_by_properties(sender=sender)

        self.assertEqual(signal.sender, sender)
        self.assertEqual(r.content_type, 'application/json')
        logging.info(r.body)
        body = json.loads(r.body)['signal']
        logging.info(body)
        self.assertEqual(body['token'], signal.token)
        self.assertEqual(body['sender'], sender)
        self.assertEqual(body['subject'], subject)
        self.assertEqual(body['receivers']['to']['to1@asdf.com'], u'蘇')
        self.assertEqual(body['receivers']['to']['to2@asdf.com'], u'K J')
        self.assertEqual(body['receivers']['cc'], {})
        self.assertEqual(body['receivers']['bcc'], {})
        self.assertEqual(body['receiver_emails'], ['to1@asdf.com', 'to2@asdf.com'])
        
    def testAccessSignal_1(self):
        sender = 'sender@asdf.com'
        self.create_user(sender)
        self.loginUser(sender)
        signal = self.create_signal(to='蘇 <to1@asdf.com>, K J <to2@asdf.com>')
        token = signal.token
        logging.info('token: %s' % token)

        r = self.testapp.get('/s/s.gif?sync=1&t=%s' % token, extra_environ={'REMOTE_ADDR': '168.95.1.1'}, xhr=True)

        access = Access.find_by_properties(token=token)
        assert access.sender == signal.sender
        assert access.accessor is None  # beacuse multiple accessor
        assert access.ass is None
        assert access.ip == '168.95.1.1'
        self.assertEqual(r.content_type, 'image/gif')
        self.assertEqual(r.body, u'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7')

    def testAccessSignal_2(self):
        """
        access with only one receiver
        """
        sender = 'sender@asdf.com'
        self.create_user(sender)
        self.loginUser(sender)
        signal = self.create_signal()
        token = signal.token
        self.testapp.get('/s/s.gif?sync=1&t=%s' % token, extra_environ={'REMOTE_ADDR': '168.95.1.1'}, xhr=True)
        signal = Signal.find_by_properties(token=signal.token)
        assert signal.access_count == 1

        access = Access.find_by_properties(token=token)
        assert access.accessor == 'to1@asdf.com'

    def testAccessSignal_3(self):
        """
        access without create user
        """
        sender = 'sender@asdf.com'
        # self.create_user(sender)
        # self.loginUser(sender)
        signal = self.create_signal(sender=sender)
        token = signal.token
        self.testapp.get(
            '/s/s.gif?sync=1&t=%s' %
            token, extra_environ={
                'REMOTE_ADDR': '168.95.1.1'}, headers={
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko)'}, xhr=True)
        signal = Signal.find_by_properties(token=signal.token)
        assert signal.access_count == 1
        self.assertEqual(signal.country, 'TW')
        self.assertEqual(signal.city, 'Taipei City')
        self.assertEqual(signal.device, 'iPhone')

        access = Access.find_by_properties(token=token)
        assert access.accessor == 'to1@asdf.com'

        # auto create user
        user = UserInfo.find_by_properties(email=sender)
        assert user is not None

    def testGetSignals(self):
        sender = 's@asdf.com'
        receiver = 'abc@asdf.com'
        self.create_signal(sender, subject='1', to='abc <%s>' % receiver)
        self.create_signal(sender, subject='2')
        self.create_signal(sender, subject='3')

        r = self.testapp.get('/resource/signals?sender=%s' % sender)
        self.assertEqual(r.status_code, 200)
        result = json.loads(r.body)
        logging.info(result)
        self.assertEqual(len(result['data']), 3)
        self.assertEqual(result['data'][0]['subject'], '3')
        self.assertEqual(result['data'][1]['subject'], '2')
        self.assertEqual(result['data'][2]['subject'], '1')
        self.assertEqual(result['data'][2]['receiver_emails'][0], receiver)

    def testCreateLink(self):
        pass

    def testAccessLink(self):
        pass

    def test_access_signal_email_sent(self):
        """
        test for
        1. first access
        2. second access
        3. within time threshold
        """
        sender = 'sender@asdf.com'
        self.create_user(sender)
        self.loginUser(sender)
        signal = self.create_signal()
        token = signal.token

        # first access
        self.testapp.get('/s/s.gif?sync=1&t=%s' % token, extra_environ={'REMOTE_ADDR': '168.95.1.1'}, xhr=True)
        messages = self.mail_stub.get_sent_messages(to='sender@asdf.com')
        self.assertEqual(1, len(messages))
        self.assertEqual('sender@asdf.com', messages[0].to)

        # second access
        self.testapp.get('/s/s.gif?sync=1&t=%s' % token, extra_environ={'REMOTE_ADDR': '168.95.1.1'}, xhr=True)
        messages = self.mail_stub.get_sent_messages(to='sender@asdf.com')
        self.assertEqual(2, len(messages))
        self.assertEqual('sender@asdf.com', messages[0].to)

        # third access
        self.testapp.get('/s/s.gif?sync=1&t=%s' % token, extra_environ={'REMOTE_ADDR': '168.95.1.1'}, xhr=True)
        messages = self.mail_stub.get_sent_messages(to='sender@asdf.com')
        signal = Signal.find_by_properties(token=token)
        assert signal.notify_triggered
        self.assertEqual(2, len(messages))
        self.assertEqual('sender@asdf.com', messages[0].to)
        
    def test_access_signal_with_templar(self):
        sender = 'sender@asdf.com'
        self.create_user(sender)
        templar = self.create_templar()
        signal = self.create_signal(templar_id=templar.tid)
        token = signal.token
        
        self.testapp.get('/s/s.gif?sync=1&t=%s' % token, extra_environ={'REMOTE_ADDR': '168.95.1.1'}, xhr=True)
        messages = self.mail_stub.get_sent_messages(to='sender@asdf.com')
        signal = Signal.find_by_properties(token=token)
        self.assertEqual(sender, messages[0].to)
        templar = Templar.find_by_properties(tid=templar.tid)
        self.assertEqual(templar.used_times, 1)
        self.assertEqual(templar.opened_times, 1)
        self.assertEqual(templar.replied_times, 0)
        
    def test_update_notification_setting(self):
        sender = 'sender@asdf.com'
        self.create_user(sender)
        self.loginUser(sender)
        signal = self.create_signal()
        token = signal.token

        code = Signal.encode_signal_token(token)
        logging.debug('code %s' % code)
        for ns in ['d', 'e', 'disable']:
            r = self.testapp.get('/settings/notification/update?c=%s&ns=%s' % (code, ns))
            logging.debug(r.body)
            assert 'Success' in r.body
            signal = Signal.find_by_properties(token=token)
            self.assertEqual(signal.notification_setting, ns)

    def test_legitimate_user_update1(self):
        controller = Signals()
        sender = 'sender@asdf.com'
        tz_offset = 9
        self.create_user(sender, tz_offset=tz_offset)
        result = controller._check_user_legit_and_create_or_update_user_last_seen_and_started(sender, tz_offset, sync=True)
        # TODO: change this
        self.assertNotEqual(result, None)
        user = UserInfo.find_by_properties(email=sender)
        self.assertEqual(user.email, sender)  # test user successfully created

    def test_legitimate_user_update2(self):
        controller = Signals()
        sender = 'sender@asdf.com'
        tz_offset = 9
        self.create_user(sender, tz_offset=tz_offset)
        result_user = controller._check_user_legit_and_create_or_update_user_last_seen_and_started(sender, tz_offset, sync=True)
        assert result_user
        assert result_user.email == sender
        assert result_user.last_seen
        assert result_user.started
        self.assertEqual(result_user.tz_offset, tz_offset)

    def test_access_from_proxy_microsoft(self):
        sender = 'sender@asdf.com'
        self.loginUser(sender)
        self.create_user(sender)
        signal = self.create_signal()
        token = signal.token

        r = self.testapp.get('/s/s.gif?sync=1&t=%s' % token, extra_environ={'REMOTE_ADDR': '65.55.1.1'}, xhr=True)
        messages = self.mail_stub.get_sent_messages(to='sender@asdf.com')
        self.assertEqual(1, len(messages))
        self.assertEqual('sender@asdf.com', messages[0].to)
        print messages[0].body.decode()
        self.assertIn('Microsoft', messages[0].body.decode())

    def test_access_from_proxy_gmail(self):
        sender = 'sender@asdf.com'
        self.loginUser(sender)
        self.create_user(sender)
        signal = self.create_signal()
        token = signal.token

        r = self.testapp.get('/s/s.gif?sync=1&t=%s' % token,
                             headers={'User-Agent': 'GoogleImageProxy'},
                             extra_environ={'REMOTE_ADDR': '168.95.1.1'}, xhr=True)
        messages = self.mail_stub.get_sent_messages(to='sender@asdf.com')
        self.assertEqual(1, len(messages))
        self.assertEqual('sender@asdf.com', messages[0].to)
        print messages[0].body.decode()
        self.assertIn('Gmail', messages[0].body.decode())

    
    def test_update_signal_replied_from_message(self):
        message = """
        {
      "historyId": "3093653", 
      "id": "14cfbf8b941e64d9", 
      "snippet": "Sincerely, Shih-Wen Su", 
      "sizeEstimate": 954, 
      "threadId": "14cfbf8b941e64d9", 
      "labelIds": [
        "SENT", 
        "INBOX", 
        "IMPORTANT", 
        "UNREAD"
      ], 
      "payload": {
        "mimeType": "multipart/alternative", 
        "headers": [
          {
            "name": "MIME-Version", 
            "value": "1.0"
          }, 
          {
            "name": "Received", 
            "value": "by 10.229.15.202 with HTTP; Mon, 27 Apr 2015 10:42:03 -0700 (PDT)"
          }, 
          {
            "name": "Date", 
            "value": "Tue, 28 Apr 2015 01:42:03 +0800"
          }, 
          {
            "name": "Delivered-To", 
            "value": "ck890358@gmail.com"
          }, 
          {
            "name": "Message-ID", 
            "value": "<CANnUM8TtdaQNrB688x33aBFjVCTn33f7FLEuwkSk9wKHL-SRSQ@mail.gmail.com>"
          }, 
          {
            "name": "Subject", 
            "value": "test mail"
          }, 
          {
            "name": "From", 
            "value": "Shih-Wen Su <ck890358@gmail.com>"
          }, 
          {
            "name": "To", 
            "value": "Shih-Wen Su <sushi@zenblip.com>"
          }, 
          {
            "name": "Content-Type", 
            "value": "multipart/alternative; boundary=001a113a36b28f21c30514b84317"
          }
        ], 
        "parts": [
          {
            "mimeType": "text/plain", 
            "headers": [
              {
                "name": "Content-Type", 
                "value": "text/plain; charset=UTF-8"
              }
            ], 
            "body": {
              "data": "U2luY2VyZWx5LA0KU2hpaC1XZW4gU3UNCg==", 
              "size": 25
            }, 
            "partId": "0", 
            "filename": ""
          }, 
          {
            "mimeType": "text/html", 
            "headers": [
              {
                "name": "Content-Type", 
                "value": "text/html; charset=UTF-8"
              }
            ], 
            "body": {
              "data": "PGRpdiBkaXI9Imx0ciI-PGJyIGNsZWFyPSJhbGwiPjxkaXY-PGRpdiBjbGFzcz0iZ21haWxfc2lnbmF0dXJlIj48ZGl2IGRpcj0ibHRyIj5TaW5jZXJlbHksPGJyPlNoaWgtV2VuIFN1PGJyPjwvZGl2PjwvZGl2PjwvZGl2Pg0KPC9kaXY-PGRpdiBzdHlsZT0iZmxvYXQ6cmlnaHQiIHJlbD0iX196YnRrX18iPjxpbWcgc3JjPSJodHRwOi8vd3d3LmVtYWlsLWxpbmsuY29tL3Mvcy5naWY_dT01OTFkMzAxNiZhbXA7dD00NWEwOGE2OTM0ZWVhOGJlNjNhNCIgd2lkdGg9IjAiIGhlaWdodD0iMCIgc3R5bGU9ImRpc3BsYXk6bm9uZTtvcGFjaXR5OjAiPjwvZGl2Pg0K", 
              "size": 318
            }, 
            "partId": "1", 
            "filename": ""
          }
        ], 
        "body": {
          "size": 0
        }, 
        "filename": ""
      }
    }
    """
        s = self.create_signal()
        s.update_signal_replied_from_message(json.loads(message))
        self.assertTrue(s.replied)
        
    def test_create_signal_with_templar(self):
        t = self.create_templar()
        self.create_signal(templar_id=t.tid)
        self.assertEqual(t.used_times, 1)
        
        