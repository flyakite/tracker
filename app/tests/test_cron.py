'''
Created on 2014/9/8

@author: sushih-wen
'''
import base64
import json
import logging
from datetime import datetime, timedelta
from google.appengine.ext import testbed
from ferrisnose import AppEngineTest, AppEngineWebTest, FerrisAppTest
from app.models.signal import Signal
from app.models.access import Access
from app.models.report_group import ReportGroup
from app.models.user_info import UserInfo
from app.controllers.cron import Cron


_ADMIN_EMAIL = 'sushi@zenblip.com'


class TestCronController(AppEngineWebTest):

    """

    def post(self, url, params='', headers=None, extra_environ=None,
             status=None, upload_files=None, expect_errors=False,
             content_type=None, xhr=False):

        Do a POST request. Similar to :meth:`~webtest.TestApp.get`.

        :param params:
            Are put in the body of the request. If params is a
            iterator it will be urlencoded, if it is string it will not
            be encoded, but placed in the body directly.

            Can be a collections.OrderedDict with
            :class:`webtest.forms.Upload` fields included::


            app.post('/myurl', collections.OrderedDict([
                ('textfield1', 'value1'),
                ('uploadfield', webapp.Upload('filename.txt', 'contents'),
                ('textfield2', 'value2')])))

        :param upload_files:
            It should be a list of ``(fieldname, filename, file_content)``.
            You can also use just ``(fieldname, filename)`` and the file
            contents will be read from disk.
        :type upload_files:
            list
        :param content_type:
            HTTP content type, for example `application/json`.
        :type content_type:
            string

        :param xhr:
            If this is true, then marks response as ajax. The same as
            headers={'X-REQUESTED-WITH': 'XMLHttpRequest', }
        :type xhr:
            boolean

        :returns: :class:`webtest.TestResponse` instance.

    """

    def setUp(self):
        AppEngineWebTest.setUp(self)
        self.add_controller(Cron)
        self.mail_stub = self.testbed.testbed.get_stub(testbed.MAIL_SERVICE_NAME)
        self.taskqueue_stub = self.testbed.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)

    def testIntervalReport(self):
        # TODO: add dummy signals and accesses
        r = self.testapp.get('/cron/interval_report?sync=1&start=2-0-0')
        logging.debug(r)
        r = self.testapp.get('/cron/interval_report?sync=1&start=1-0-0&daily=1')
        logging.debug(r)
        r = self.testapp.get('/cron/interval_report?sync=1&start=7-3-0&end=0-3-0&weekly=1')
        logging.debug(r)

    def testIntervalReportWithReportGroup(self):
        # TODO: add dummy signals and accesses
        email = 'sushi@zenblip.com'
        org = 'test'
        rg = ReportGroup(
            rgid='test',
            orgs=[org, 'hk'],
            to=[email, 'sushi2@zenblip.com']
        )
        rg.put()

        sender = 'user1@asdf.com'
        userinfo = UserInfo(
            email=sender,
            orgs=[org],
        )
        userinfo.put()
        r = self.testapp.get('/cron/interval_report?sync=1&rgid=test&start=1-0-0')
        logging.debug(r)
        tasks = self.taskqueue_stub.get_filtered_tasks(url='/cron/interval_report_personal')
        self.assertEqual(1, len(tasks))

    def testIntervalReportWithReportGroupPersonal(self):
        email = 'manager1@asdf.com'
        org = 'test'
        rgid = 'test'
        rg = ReportGroup(
            rgid=rgid,
            orgs=[org, 'hk'],
            to=[email, 'manager2@asdf.com']
        )
        rg.put()

        sender = 'user1@asdf.com'
        userinfo = UserInfo(
            email=sender,
            orgs=[org],
        )
        userinfo.put()
        token = '123kh4kj3h454'
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
            token=token,
            sender=sender,
            kind='open',
            device='iPhone',
            accessor=to1
        )
        access.put()
        start = datetime.utcnow() - timedelta(days=1, hours=1)
        end = datetime.utcnow()
        start = base64.urlsafe_b64encode(start.isoformat())
        end = base64.urlsafe_b64encode(end.isoformat())
        r = self.testapp.post('/cron/interval_report_personal?sync=1',
                              params={
                                  'start': start,
                                  'end': end,
                                  'rgid': rgid,
                                  'sender': sender
                              }
                              )
        logging.debug(r)
        messages = self.mail_stub.get_sent_messages(to=email)
        self.assertEqual(1, len(messages))

        r = self.testapp.get('/cron/interval_report?org=%s&start=1-0-0&end=0-0-0&daily=1' % org)
        logging.debug(r)
        self.assertEqual(r.status_code, 200)

        # test debug mode
        r = self.testapp.post('/cron/interval_report_personal?sync=1',
                              params={
                                  'start': start,
                                  'end': end,
                                  'rgid': rgid,
                                  'sender': sender,
                                  'debug': 1
                              }
                              )
        messages = self.mail_stub.get_sent_messages(to=_ADMIN_EMAIL)
        self.assertEqual(1, len(messages))

    def testActivityCompileReport(self):
        email = 'user1@asdf.com'
        userinfo = UserInfo(
            email=email,
            orgs=['test'],
        )
        userinfo.put()

        r = self.testapp.get('/cron/activity_report?sync=1&org=test&start=1-3-0&end=0-3-0')
        logging.debug(r)

        messages = self.mail_stub.get_sent_messages(to=email)
        self.assertEqual(1, len(messages))
        self.assertEqual(email, messages[0].to)
