# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime, timedelta
from uuid import uuid4
from google.appengine.ext import testbed
from ferrisnose import AppEngineTest, AppEngineWebTest, FerrisAppTest
from app.models.signal import Signal
from app.models.access import Access
from app.controllers.accesses import Accesses, AccessNotification


class TestAccesses(AppEngineWebTest):

    """
    test
    """

    def setUp(self):
        AppEngineWebTest.setUp(self)
        self.add_controller(Accesses)
        self.mail_stub = self.testbed.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def testDelayedAccessNotification(self):
        token = 'asdkjfh234'
        sender = 'sender@asdf.com'
        to1 = 'to1@asdf.com'
        signal = Signal(
            token=token,
            sender=sender,
            receivers={'to': {to1: 'John'}},
            subject='test subject',
            access_count=2,
            tz_offset=9,
        )
        signal.put()

        access = Access(
            parent=signal.key,
            token=token,
            sender=sender,
            kind='open',
            device='iPhone',
            accessor=to1
        )
        access.put()
        signal.notify_triggered = access.created
        signal.put()

        r = self.testapp.post('/tasks/delayed_access_notification',
                              {'token': token,
                               'access_id': access.key.id(),
                               'sync': 1
                               }
                              )
        logging.debug(r)
        assert r.status_code == 200
        messages = self.mail_stub.get_sent_messages(to=sender)
        self.assertEqual(1, len(messages))
