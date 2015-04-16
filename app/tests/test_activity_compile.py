# -*- coding: utf-8 -*-
'''
Created on 2014/9/8

@author: sushih-wen
'''
import json
import logging
from datetime import datetime, timedelta
from ferrisnose import AppEngineTest, AppEngineWebTest, FerrisAppTest
from app.models.signal import Signal
from app.models.access import Access
from app.models.activity_compile import ActivityCompile
from app.controllers.activity_compiles import ActivityCompiles
from app.controllers.auths import encode_token, decode_token


class TestEncrypt(AppEngineWebTest):

    """
    test
    """

    def setUp(self):
        AppEngineWebTest.setUp(self)

    def testEncryptDecrypt(self):
        ac = ActivityCompile(
            senders=['sender@asdf.com'],
            start=datetime.utcnow() - timedelta(days=1),
            end=datetime.utcnow(),
        )
        ac.put()
        code = ActivityCompile.encrypt_activity_compile_to_code(ac)
        logging.debug(code)
        assert len(code) < 1900  # approximate max URL length
        new_ac = ActivityCompile.decrypt_code_to_activity_compile(code)
        self.assertEqual(new_ac.senders, ac.senders)
        self.assertEqual(new_ac.start, ac.start)


class TestActivityCompileController(FerrisAppTest):

    def testActivityCompile(self):
        sender = 'sender@asdf.com'
        start = datetime.utcnow() - timedelta(days=1)
        end = datetime.utcnow()
        ac = ActivityCompile(
            senders=[sender],
            start=start,
            end=end,
        )
        ac.put()
        signal = Signal(
            token='123kh4kj3h454',
            sender=sender,
            receivers={'to': {'to1@asdf.com': ''}},
            subject='test',
            access_count=2
        )
        signal.put()
        signal2 = Signal(
            token='123kh4kj3h454',
            sender=sender,
            receivers={'to': {'to1@asdf.com': ''}},
            subject=u'中文',
            access_count=2
        )
        signal2.put()

        signal.created = datetime.utcnow() - timedelta(hours=1)
        signal.put()
        code = ActivityCompile.encrypt_activity_compile_to_code(ac)
        r = self.testapp.get('/activity_report?c=%s' % code)
        self.assertEqual(r.content_type, 'application/csv')

        # new way
        activity_compile_token = encode_token({'sender': sender, 'start': start.isoformat(), 'end': end.isoformat()})
        r = self.testapp.get('/activity_report?t=%s' % activity_compile_token)
