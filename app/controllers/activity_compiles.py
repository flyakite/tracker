# -*- coding: utf-8 -*-
'''
Created on 2014/10/5

@author: sushih-wen
'''

import json
import re
import random
import logging
import csv
import webapp2
import base64
from datetime import datetime, timedelta
from uuid import uuid4
from urllib import urlencode
from google.appengine.api import memcache, urlfetch, channel
from google.appengine.ext import deferred, ndb
from ferris import route_with
from ferris.core import mail
from app.models.link import Link
from app.models.access import Access
from app.models.signal import Signal
from app.models.user_track import UserTrack
from app.models.activity_compile import ActivityCompile
from base import BaseController, BaseView
from ferris import settings
from auths import decode_token

class ActivityCompiles(webapp2.RequestHandler):
    # class ActivityCompiles(BaseController):

    """
    Dynamic output a csv file
    """
    #  route with /activity_report

    def get(self):

        name = self.request.get('n')
        code = self.request.get('c')
        if code:
            ac = ActivityCompile.decrypt_code_to_activity_compile(code)
        else:
            token = self.request.get('t')
            data = decode_token(token)
            start = datetime.strptime(base64.urlsafe_b64decode(data['start']), '%Y-%m-%dT%H:%M:%S.%f')
            end = datetime.strptime(base64.urlsafe_b64decode(data['end']), '%Y-%m-%dT%H:%M:%S.%f')
            ac = ActivityCompile(
                            senders = [data['sender']],
                            start = start,
                            end = end
                            )
            

        if not ac:
            self.abort(404)
            return

        signals = Signal.query(Signal.sender.IN(ac.senders),
                               Signal.created > ac.start,
                               Signal.created < ac.end).fetch()

        if not name and ac.start and ac.end:
            name = 'zenblip_Activity_Report_UTC_%s_%s' % (datetime.strftime(ac.start, '%Y-%m-%d_%H:%M'),
                                                          datetime.strftime(ac.end, '%Y-%m-%d_%H:%M'))

        logging.info('senders')
        logging.info(ac.senders)
        logging.info('start %s, end: %s' % (ac.start, ac.end))

        # TODO: deal with cache later
        #self.response.headers['cache-control'] = 'nocache'
        self.response.content_type = 'application/csv'
        self.response.headers['Content-Disposition'] = 'attachment; filename=%s.csv' % name

        writer = csv.writer(self.response.out)
        writer.writerow(['Receiver', 'Subject', 'Opened', 'Frequency'])
        signals = sorted(signals, key=lambda x: x.access_count, reverse=True)
        logging.info('signals:')
        for s in signals:
            if s.receivers.get('to'):
                r = s.receivers.get('to').keys()[0]
            else:
                r = ''
            opened = 'Y' if s.access_count > 0 else 'N'
            if isinstance(s.subject, unicode):
                logging.info(s.subject)
                subject = s.subject.encode('utf-8')
            else:
                subject = s.subject
            writer.writerow([r, subject, opened, s.access_count])
