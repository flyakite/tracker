# -*- coding: utf-8 -*-
'''
Created on 2014/9/8

@author: sushih-wen
'''

import json
import re
import logging
import base64
import operator
from datetime import datetime, timedelta
from uuid import uuid4
from urllib import urlencode
from google.appengine.api import users, urlfetch, memcache, taskqueue
from google.appengine.ext import deferred, ndb
from ferris import route_with
from ferris.core import mail
from app.models.link import Link
from app.models.access import Access
from app.models.signal import Signal
from app.models.user_info import UserInfo
from app.models.activity_compile import ActivityCompile
from app.models.report_group import ReportGroup
from app.models.setting import Setting
from base import BaseController
from auths import encode_token, decode_token
from ferris import settings


_ADMINS = ['sushi@zenblip.com']
# _ADMINS = ['sushi@zenblip.com', 'christopher@zenblip.com']


def to_timedelta(fmt):
    # class datetime.timedelta([days[, seconds[, microseconds[, milliseconds[, minutes[, hours[, weeks]]]]]]])
    """
    '%d-%H-%M'
    """
    logging.info('to_timedelta %s' % fmt)
    days, hours, minutes = fmt.split('-')
    return timedelta(days=int(days), hours=int(hours), minutes=int(minutes))

    
class SubscriptionReport(object):
    pass
    
class Cron(BaseController):

    def query_user_emails(self, start, end, rgid=None, org=None):
        # TODO: circuler query
        if rgid:
            rg = ReportGroup.find_by_properties(rgid=rgid)
            if not rg:
                logging.error('rg not found: %s' % rgid)
                return
            userinfos = UserInfo.query(UserInfo.orgs.IN(rg.orgs)).fetch()
            unique_user_emails = list(set([u.email for u in userinfos]))

        elif org:
            userinfos = UserInfo.query(UserInfo.orgs == org).fetch()
            logging.info('userinfo query length: %s' % len(userinfos))
            unique_user_emails = list(set([u.email for u in userinfos]))

        else:
            signals = Signal.query(Signal.created > start, Signal.created < end).fetch()
            logging.info('signals query length: %s' % len(signals))
            unique_user_emails = list(set([s.sender for s in signals]))

        return unique_user_emails

    @route_with('/cron/interval_report')
    def interval_report(self):
        self.meta.change_view('json')

        sync = self.request.get('sync')
        debug = self.request.get('debug')
        if debug:
            logging.info('DEBUG')
        daily = self.request.get('daily')
        weekly = self.request.get('weekly')
        rgid = self.request.get('rgid')  # report group id
        org = self.request.get('org')  # org that wants to receive the report
        start = self.request.get('start')  # start deltatime from the time report is generating. '%d-%H-%M'
        end = self.request.get('end')  # end deltatime from the time report is generating. '%d-%H-%M'
        # TODO: adjust start and end for timezone
        logging.info('start: %s ,end: %s' % (start, end))
        utcnow = datetime.utcnow()
        logging.info('utcnow: %s' % utcnow.isoformat())

        start = utcnow - to_timedelta(start)
        end = utcnow - to_timedelta(end) if end else utcnow  # if end is not specified, use now
        logging.info('UTC start: %s ,end: %s' % (start.isoformat(), end.isoformat()))

        user_emails = self.query_user_emails(start, end, rgid=rgid, org=org)
        logging.info('query_user_emails:')
        logging.info(user_emails)
        start = base64.urlsafe_b64encode(start.isoformat())
        end = base64.urlsafe_b64encode(end.isoformat())
        for sender in user_emails:
            logging.info('sending to %s' % sender)
            taskqueue.add(url='/cron/interval_report_personal',
                          params={
                              'sender': sender,
                              'start': start,
                              'end': end,
                              'sync': sync,
                              'debug': debug,
                              'daily': daily,
                              'weekly': weekly,
                              'rgid': rgid,
                              'org': org
                          })

        self.context['data'] = user_emails

    @route_with('/cron/interval_report_personal')
    def interval_report_personal(self):
        """
        by sender
        """
        self.meta.change_view('json')
        _high_frequency_email_count = 3

        sync = self.request.get('sync')
        debug = self.request.get('debug')
        daily = self.request.get('daily')
        weekly = self.request.get('weekly')
        rgid = self.request.get('rgid')
#         org = self.request.get('org')

        sender = self.request.get('sender')
        logging.info(sender)

        start = str(self.request.get('start'))
        end = str(self.request.get('end'))
        logging.info('start: %s ,end: %s' % (start, end))

        start = datetime.strptime(base64.urlsafe_b64decode(start), '%Y-%m-%dT%H:%M:%S.%f')  # isoformat
        end = datetime.strptime(base64.urlsafe_b64decode(end), '%Y-%m-%dT%H:%M:%S.%f')
        logging.info('UTC start: %s, end: %s' % (start.isoformat(), end.isoformat()))

        self.context['data'] = {
            'sender': sender,
            'start': start,
            'end': end
        }

        # signals statistics
        signals = Signal.query(Signal.sender == sender, Signal.created > start, Signal.created < end) \
                        .order(Signal.created) \
                        .fetch()
        if not signals:
            logging.warning('no signals')
            return

        last_signal = signals[-1]
        tz_offset = last_signal.tz_offset or 0

        number_of_emails_tracked = len(signals)
        emails_not_opened = filter(lambda x: x.access_count == 0, signals)
        number_of_emails_not_opened = len(emails_not_opened)
        open_rate = 1 - 1.0 * number_of_emails_not_opened / number_of_emails_tracked
        sort_by_access_count = sorted(signals, key=lambda x: x.access_count, reverse=True)
        high_access_frequency_signals = sort_by_access_count[:_high_frequency_email_count]

        logging.info('open_rate: %s' % open_rate)
        logging.info('number_of_emails_tracked: %s' % number_of_emails_tracked)
        logging.info('high_access_frequency_signals: %s' % high_access_frequency_signals)

        # This is not consistent
        # accesses = Access.query(Access.sender == sender, Access.created > start, Access.created > end) \
        #                  .fetch(10000)

        # Query Access
#         accesses = []
#         for signal in signals:
#             logging.info(signal)
#             if signal.access_count > 0:
#                 accs = Access.query(ancestor=signal.key) \
#                         .filter(Access.created > start,
#                                 Access.created > end) \
#                                 .fetch(10000)
#                 accesses.extend(accs)

        signal_tokens = [s.token for s in signals]
        accesses = Access.query(Access.token.IN(signal_tokens)).fetch()

        if not accesses:
            logging.warning('no access')

        if accesses:
            accesses_count = len(accesses)
            accesses_by_token = {}
            time_frame_text = {'weekdays': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                               # every three hours
                               #                                'frames': ['12:00am', '03:00am', '06:00am', '09:00am',
                               #                                           '12:00pm', '03:00pm', '06:00pm', '09:00pm', '12:00am']
                               'frames': ['12:00am', '01:00am', '02:00am', '03:00am', '04:00am', '05:00am',
                                          '06:00am', '07:00am', '08:00am', '09:00am', '10:00am', '11:00am',
                                          '12:00pm', '01:00pm', '02:00pm', '03:00pm', '04:00pm', '05:00pm',
                                          '06:00pm', '07:00pm', '08:00pm', '09:00pm', '10:00pm', '11:00pm', '12:00am']
                               }
            time_frame = {0: {},  # Mon
                          1: {},  # Tue
                          2: {},
                          3: {},
                          4: {},
                          5: {},
                          6: {}
                          }
            device_count = {}
            """
            time frame contains
            
            ex:
            time_frame
            {
                0:{ #per day
                    0:{ #per time frame (1 hour)
                        'count': 5,
                        'devices':{
                            'iphone':2,
                            'Windows':3,
                             },
                        'max_device': 'iphone'
                        },
                    1:{
                        'count': 10,
                        'devices':{
                            ...
                        }
                    },
                    ...
                    'sum': 16,
                    'max_i': 1,    //max time frame index of this day
                    'portion': 0.23, //percentage of this day over this week
                },
                1:{
                    ...
                },
                ...
            
            }
            """
            for a in accesses:
                if a.token not in accesses_by_token:
                    accesses_by_token[a.token] = [a]
                else:
                    accesses_by_token[a.token].append(a)

                a.created = a.created + timedelta(hours=tz_offset)

                # categorize accesses into 8 time-frames(3 hours each)
                # 00:00 - 03:00 - 06:00 - 09:00 - 12:00 - 15:00 - 18:00 - 21:00 - 24:00
                # in datetime, Monday is 0 and Sunday is 6
                # UPDATE:
                # categorize accesses into 12 time-frames(every 1 hour)
                w_index = a.created.weekday()
                assert w_index in range(7)
                # tf_index = a.created.hour // 3
                tf_index = a.created.hour
                if tf_index not in time_frame[w_index]:
                    time_frame[w_index][tf_index] = {}
                    time_frame[w_index][tf_index]['count'] = 1
                else:
                    time_frame[w_index][tf_index]['count'] += 1

                if a.device:
                    # TODO: setup a object class for device count
                    # calculate devices for every time frame period
                    if not time_frame[w_index][tf_index].get('devices'):
                        time_frame[w_index][tf_index]['devices'] = {a.device: 1}
                    elif not time_frame[w_index][tf_index]['devices'].get(a.device):
                        time_frame[w_index][tf_index]['devices'][a.device] = 1
                    else:
                        time_frame[w_index][tf_index]['devices'][a.device] += 1

                    # calculate devices
                    if a.device not in device_count:
                        device_count[a.device] = 1
                    else:
                        device_count[a.device] += 1

            logging.info('device_count %s' % device_count)
            logging.info('time_frame %s' % time_frame)

            # find sum and max of each weekday
            sum_of_all = 0
            for wi, tf in time_frame.iteritems():
                sum_count = 0
                max_count = 0
                max_tfi = 0
                logging.info("wi: %s, tf: %s" % (wi, tf))
                for tfi, tf_statistics in tf.iteritems():
                    sum_count += tf_statistics['count']
                    if tf_statistics['count'] > max_count:  # TODO: deal with equal
                        max_count = tf_statistics['count']
                        max_tfi = tfi
                    try:
                        if tf_statistics['devices']:
                            max_di = max(tf_statistics['devices'].iteritems(), key=operator.itemgetter(1))[0]
                            time_frame[wi][tfi]['max_device'] = max_di
                    except:
                        pass
                time_frame[wi]['sum'] = sum_count
                time_frame[wi]['max_i'] = max_tfi
                sum_of_all += sum_count

            for wi, tf in time_frame.iteritems():
                if time_frame[wi]:
                    time_frame[wi]['portion'] = 1.0 * time_frame[wi]['sum'] / sum_of_all

            logging.info(time_frame)

            # statistics of devices
            try:
                top_devices_list = sorted(device_count, key=lambda x: device_count[x], reverse=True)[:3]
            except:
                top_devices_list = device_count.keys()[:3]
            logging.info('top_devices_list')
            logging.info(top_devices_list)

            if daily:
                subject = 'zenblip Daily Report'
            elif weekly:
                subject = 'zenblip Weekly Report'
            else:
                subject = 'zenblip Report'

            if debug:
                subject += ' debug'
            logging.info('subject %s' % subject)

            if rgid:
                rg = ReportGroup.find_by_properties(rgid=rgid)
                if not rg:
                    logging.error('no report group %s' % rgid)
                    return
                receiver = rg.to
            else:
                receiver = sender

            if debug:
                logging.info('debug mode, send to admin')
                receiver = _ADMINS

            logging.info('receiver %s' % receiver)

            args = [receiver, subject]
            kwargs = dict(template_name='interval_report',
                          context={'start': start,
                                   'end': end,
                                   'open_rate': open_rate,
                                   'number_of_emails_tracked': number_of_emails_tracked,
                                   'high_access_frequency_signals': high_access_frequency_signals,
                                   'time_frame': time_frame,
                                   'time_frame_text': time_frame_text,
                                   'device_count': device_count,
                                   'top_devices_list': top_devices_list,
                                   'accesses_count': accesses_count,
                                   'daily': daily,
                                   'weekly': weekly,
                                   'rgid': rgid,
                                   'sender': sender,
                                   'debug': debug})

            if sync:
                mail.send_template(*args, **kwargs)
            else:
                # Pickling of datastore_query.PropertyOrder is unsupported.
                deferred.defer(mail.send_template, *args, **kwargs)
    
    ########## NEW ############
    def query_subscriptions(self):
        uri = 'https://www.zenblip.com/api/subscription'
        query_string = {
               'fields': 'id'
        }
        query_string = urlencode(query_string)
        try:
            result = urlfetch.fetch(uri)
            if result.status_code == 200:
                return result.content
            else:
                #simple retry
                result = urlfetch.fetch(uri)
                if result.status_code == 200:
                    return result.content
                else:
                    logging.error("query_subscriptions status:%s %s" % (result.status_code, result.content))
                    return None

        except urlfetch.DownloadError as e:
            logging.error("query_subscriptions fetch DownloadError")
            logging.error(e)
            return None
            
    def parse_subscription_ids(self, data):
        """
        [{'id': 2}]
        """
        try:
            jdata = json.loads(data)['data']
            return [sub['id'] for sub in jdata]
        except Exception as e:
            logging.error("parse_subscriptions exception: %s" % data)
            logging.error(e)
            return None
        
    def query_subscription_report(self, sub_id):
        uri = 'https://www.zenblip.com/api/subscription_report'
        try:
            result = urlfetch.fetch(uri)
            if result.status_code == 200:
                return result.content
            else:
                #simple retry
                result = urlfetch.fetch(uri)
                if result.status_code == 200:
                    return result.content
                else:
                    logging.error("query_subscription_report status:%s %s" % (result.status_code, result.content))
                    return None
        except urlfetch.DownloadError as e:
            logging.error("query_subscription_report fetch DownloadError")
            logging.error(e)
            return None

        
    def parse_subscriptions_report_emails(self, data):
        """
        {
            user_plans: [{'id': 1, 'email': u'user@test.com'}, {'id': 2, 'email': u'833bfc47@test.com'}],
            report_groups: [{'id': 1, 'emails': u'manager1@asdf.com,manager2@asdf.com'}]
        }
        """
        try:
            jdata = json.loads(data)['data']
            sr = SubscriptionReport()
            user_plan_emails = [up['email'] for up in jdata['user_plans']]
            sr.user_plan_emails = list(set(user_plan_emails))
            report_group_emails = []
            for up in jdata['report_group']:
                report_group_emails.extend(up['emails'].split(','))
            sr.report_group_emails = list(set(report_group_emails))
            return sr
            
        except Exception as e:
            logging.error("parse_subscriptions_report exception: %s" % data)
            logging.error(e)
            return None
            
    ########## NEW ############
    @route_with('/cron/new_interval_report')
    def new_interval_report(self):
        self.meta.change_view('json')

        sync = self.request.get('sync')
        debug = self.request.get('debug')
        if debug:
            logging.info('DEBUG')
        daily = self.request.get('daily')
        weekly = self.request.get('weekly')
        start = self.request.get('start')  # start deltatime from the time report is generating. '%d-%H-%M'
        end = self.request.get('end')  # end deltatime from the time report is generating. '%d-%H-%M'
        # TODO: adjust start and end for timezone
        logging.info('start: %s ,end: %s' % (start, end))
        utcnow = datetime.utcnow()
        logging.info('utcnow: %s' % utcnow.isoformat())

        start = utcnow - to_timedelta(start)
        end = utcnow - to_timedelta(end) if end else utcnow  # if end is not specified, use now
        logging.info('UTC start: %s ,end: %s' % (start.isoformat(), end.isoformat()))

        data = self.query_subscriptions()
        sub_ids = self.parse_subscription_ids(data)
        
        start = base64.urlsafe_b64encode(start.isoformat())
        end = base64.urlsafe_b64encode(end.isoformat())
        for sub_id in sub_ids:
            logging.info('querying subscription id: %s' % sub_id)
            taskqueue.add(url='/cron/dispatch_subscription_report_emails',
                          params={
                              'sub_id': sub_id,
                              'start': start,
                              'end': end,
                              'sync': sync,
                              'debug': debug,
                              'daily': daily,
                              'weekly': weekly,
                          })
        self.context['data'] = {'sub_ids':sub_ids}
         
         
    ########## NEW ############
    @route_with('/cron/dispatch_subscription_report_emails')
    def dispatch_subscription_report_emails(self):
        self.meta.change_view('json')

        sync = self.request.get('sync')
        debug = self.request.get('debug')
        if debug:
            logging.info('DEBUG')
        daily = self.request.get('daily')
        weekly = self.request.get('weekly')
        start = self.request.get('start')
        end = self.request.get('end')
        sub_id = self.request.get('sub_id')
        
        data = self.query_subscription_report(sub_id)
        sr = self.parse_subscriptions_report_emails(data)
        
        for sender in sr.user_plan_emails:
            logging.info('sending to %s' % sender)
            taskqueue.add(url='/cron/new_interval_report_personal',
                          params={
                              'sender': sender,
                              'reportgroup': ','.join(sr.report_group_emails),
                              'start': start,
                              'end': end,
                              'sync': sync,
                              'debug': debug,
                              'daily': daily,
                              'weekly': weekly,
                          })

        self.context['data'] = {'user_plan_emails':sr.user_plan_emails}

    ########## NEW ############
    @route_with('/cron/new_interval_report_personal')
    def new_interval_report_personal(self):
        """
        by sender
        """
        self.meta.change_view('json')
        _high_frequency_email_count = 3

        sync = self.request.get('sync')
        debug = self.request.get('debug')
        daily = self.request.get('daily')
        weekly = self.request.get('weekly')
        reportgroup = self.request.get('reportgroup')
        
        sender = self.request.get('sender')
        logging.info(sender)

        start = str(self.request.get('start'))
        end = str(self.request.get('end'))
        logging.info('start: %s ,end: %s' % (start, end))
        activity_report_code = encode_token({'email': sender, 'start':start, 'end':end})
        
        start = datetime.strptime(base64.urlsafe_b64decode(start), '%Y-%m-%dT%H:%M:%S.%f')  # isoformat
        end = datetime.strptime(base64.urlsafe_b64decode(end), '%Y-%m-%dT%H:%M:%S.%f')
        logging.info('UTC start: %s, end: %s' % (start.isoformat(), end.isoformat()))

        self.context['data'] = {
            'sender': sender,
            'start': start,
            'end': end
        }

        # user setting
        user_setting = Setting.query(Setting.email == sender).fetch()
        if not reportgroup:
            if daily and not user_setting.is_daily_report:
                logging.warning('setting no daily report needs to be sent')
                return
            elif weekly and not user_setting.is_weekly_report:
                logging.warning('setting no weekly report needs to be sent')
                return
                
        # signals statistics
        signals = Signal.query(Signal.sender == sender, Signal.created > start, Signal.created < end) \
                        .order(Signal.created) \
                        .fetch()
        if not signals:
            logging.warning('no signals')
            return

        
        last_signal = signals[-1]
        tz_offset = last_signal.tz_offset or 0

        number_of_emails_tracked = len(signals)
        emails_not_opened = filter(lambda x: x.access_count == 0, signals)
        number_of_emails_not_opened = len(emails_not_opened)
        open_rate = 1 - 1.0 * number_of_emails_not_opened / number_of_emails_tracked
        sort_by_access_count = sorted(signals, key=lambda x: x.access_count, reverse=True)
        high_access_frequency_signals = sort_by_access_count[:_high_frequency_email_count]

        logging.info('open_rate: %s' % open_rate)
        logging.info('number_of_emails_tracked: %s' % number_of_emails_tracked)
        logging.info('high_access_frequency_signals: %s' % high_access_frequency_signals)

        # This is not consistent
        # accesses = Access.query(Access.sender == sender, Access.created > start, Access.created > end) \
        #                  .fetch(10000)

        # Query Access
#         accesses = []
#         for signal in signals:
#             logging.info(signal)
#             if signal.access_count > 0:
#                 accs = Access.query(ancestor=signal.key) \
#                         .filter(Access.created > start,
#                                 Access.created > end) \
#                                 .fetch(10000)
#                 accesses.extend(accs)

        signal_tokens = [s.token for s in signals]
        accesses = Access.query(Access.token.IN(signal_tokens)).fetch()

        if not accesses:
            logging.warning('no access')

        if accesses:
            accesses_count = len(accesses)
            accesses_by_token = {}
            time_frame_text = {'weekdays': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                               # every three hours
                               #                                'frames': ['12:00am', '03:00am', '06:00am', '09:00am',
                               #                                           '12:00pm', '03:00pm', '06:00pm', '09:00pm', '12:00am']
                               'frames': ['12:00am', '01:00am', '02:00am', '03:00am', '04:00am', '05:00am',
                                          '06:00am', '07:00am', '08:00am', '09:00am', '10:00am', '11:00am',
                                          '12:00pm', '01:00pm', '02:00pm', '03:00pm', '04:00pm', '05:00pm',
                                          '06:00pm', '07:00pm', '08:00pm', '09:00pm', '10:00pm', '11:00pm', '12:00am']
                               }
            time_frame = {0: {},  # Mon
                          1: {},  # Tue
                          2: {},
                          3: {},
                          4: {},
                          5: {},
                          6: {}
                          }
            device_count = {}
            """
            time frame contains
            
            ex:
            time_frame
            {
                0:{ #per day
                    0:{ #per time frame (1 hour)
                        'count': 5,
                        'devices':{
                            'iphone':2,
                            'Windows':3,
                             },
                        'max_device': 'iphone'
                        },
                    1:{
                        'count': 10,
                        'devices':{
                            ...
                        }
                    },
                    ...
                    'sum': 16,
                    'max_i': 1,    //max time frame index of this day
                    'portion': 0.23, //percentage of this day over this week
                },
                1:{
                    ...
                },
                ...
            
            }
            """
            for a in accesses:
                if a.token not in accesses_by_token:
                    accesses_by_token[a.token] = [a]
                else:
                    accesses_by_token[a.token].append(a)

                a.created = a.created + timedelta(hours=tz_offset)

                # categorize accesses into 8 time-frames(3 hours each)
                # 00:00 - 03:00 - 06:00 - 09:00 - 12:00 - 15:00 - 18:00 - 21:00 - 24:00
                # in datetime, Monday is 0 and Sunday is 6
                # UPDATE:
                # categorize accesses into 12 time-frames(every 1 hour)
                w_index = a.created.weekday()
                assert w_index in range(7)
                # tf_index = a.created.hour // 3
                tf_index = a.created.hour
                if tf_index not in time_frame[w_index]:
                    time_frame[w_index][tf_index] = {}
                    time_frame[w_index][tf_index]['count'] = 1
                else:
                    time_frame[w_index][tf_index]['count'] += 1

                if a.device:
                    # TODO: setup a object class for device count
                    # calculate devices for every time frame period
                    if not time_frame[w_index][tf_index].get('devices'):
                        time_frame[w_index][tf_index]['devices'] = {a.device: 1}
                    elif not time_frame[w_index][tf_index]['devices'].get(a.device):
                        time_frame[w_index][tf_index]['devices'][a.device] = 1
                    else:
                        time_frame[w_index][tf_index]['devices'][a.device] += 1

                    # calculate devices
                    if a.device not in device_count:
                        device_count[a.device] = 1
                    else:
                        device_count[a.device] += 1

            logging.info('device_count %s' % device_count)
            logging.info('time_frame %s' % time_frame)

            # find sum and max of each weekday
            sum_of_all = 0
            for wi, tf in time_frame.iteritems():
                sum_count = 0
                max_count = 0
                max_tfi = 0
                logging.info("wi: %s, tf: %s" % (wi, tf))
                for tfi, tf_statistics in tf.iteritems():
                    sum_count += tf_statistics['count']
                    if tf_statistics['count'] > max_count:  # TODO: deal with equal
                        max_count = tf_statistics['count']
                        max_tfi = tfi
                    try:
                        if tf_statistics['devices']:
                            max_di = max(tf_statistics['devices'].iteritems(), key=operator.itemgetter(1))[0]
                            time_frame[wi][tfi]['max_device'] = max_di
                    except:
                        pass
                time_frame[wi]['sum'] = sum_count
                time_frame[wi]['max_i'] = max_tfi
                sum_of_all += sum_count

            for wi, tf in time_frame.iteritems():
                if time_frame[wi]:
                    time_frame[wi]['portion'] = 1.0 * time_frame[wi]['sum'] / sum_of_all

            logging.info(time_frame)

            # statistics of devices
            try:
                top_devices_list = sorted(device_count, key=lambda x: device_count[x], reverse=True)[:3]
            except:
                top_devices_list = device_count.keys()[:3]
            logging.info('top_devices_list')
            logging.info(top_devices_list)

            if daily:
                subject = 'zenblip Daily Report'
            elif weekly:
                subject = 'zenblip Weekly Report'
            else:
                subject = 'zenblip Report'


            if debug:
                subject += ' debug'
                logging.info('debug mode, send to admin')
                email_set_receivers = [_ADMINS]
            else:
                email_set_receivers = [sender]
                if reportgroup:
                    email_set_receivers.append(reportgroup.split(','))

            logging.info('subject %s' % subject)
            for receiver in email_set_receivers:

                logging.info('receiver %s' % receiver)
    
                args = [receiver, subject]
                kwargs = dict(template_name='interval_report',
                              context={'start': start,
                                       'end': end,
                                       'open_rate': open_rate,
                                       'number_of_emails_tracked': number_of_emails_tracked,
                                       'high_access_frequency_signals': high_access_frequency_signals,
                                       'time_frame': time_frame,
                                       'time_frame_text': time_frame_text,
                                       'device_count': device_count,
                                       'top_devices_list': top_devices_list,
                                       'accesses_count': accesses_count,
                                       'daily': daily,
                                       'weekly': weekly,
                                       'rgid': '1',
                                       'sender': sender,
                                       'activity_report_code': activity_report_code,
                                       'debug': debug})
    
                if sync:
                    mail.send_template(*args, **kwargs)
                    
                else:
                    # Pickling of datastore_query.PropertyOrder is unsupported.
                    deferred.defer(mail.send_template, *args, **kwargs)

    @route_with('/cron/activity_report')
    def activity_report(self):
        """
        """
        self.meta.change_view('json')

        org = self.request.get('org')
        sync = self.request.get('sync')
        debug = self.request.get('debug')
        start = self.request.get('start')  # start deltatime from the time report is generating. '%d-%H-%M'
        end = self.request.get('end')  # end deltatime from the time report is generating. '%d-%H-%M'
        if not org or not start or not end:
            logging.info('missing org or start or end')
            return
        logging.info('start: %s ,end: %s' % (start, end))
        utcnow = datetime.utcnow()
        logging.info('utcnow: %s' % utcnow.isoformat())

        start = utcnow - to_timedelta(start)
        end = utcnow - to_timedelta(end) if end else utcnow  # if end is not specified, use now
        logging.info('UTC start: %s ,end: %s' % (start.isoformat(), end.isoformat()))

        userinfos = UserInfo.query(UserInfo.orgs == org).fetch()
        logging.info('userinfos len: %s' % len(userinfos))
        for u in userinfos:
            logging.info('activity of %s' % u.email)
            ac = ActivityCompile(
                senders=[u.email],
                start=start,
                end=end
            )
            code = ActivityCompile.encrypt_activity_compile_to_code(ac)

            logging.info('code %s' % code)

            if debug:
                receiver = _ADMINS
            else:
                receiver = u.email

            subject = 'zenblip Activity Report'
            if debug:
                subject += ' debug'

            logging.info('sending to %s' % receiver)

            args = [receiver, subject]
            kwargs = dict(template_name='activity_report',
                          context={'start': start,
                                   'end': end,
                                   'code': code,
                                   'debug': debug})

            if sync:
                mail.send_template(*args, **kwargs)
            else:
                # Pickling of datastore_query.PropertyOrder is unsupported.
                deferred.defer(mail.send_template, *args, **kwargs)

        self.context['data'] = {'userinfos': len(userinfos)}

    @route_with('/cron/send_user_scheduled_emails')
    def send_user_scheduled_emails(self):
        """
        TODO: should be seperated into different timezone
        """

        logging.info('send_user_scheduled_emails')
        self.meta.change_view('json')
        sync = self.request.get('sync', False)

        longest_period = timedelta(days=15)
        users = UserInfo.query(UserInfo.started > datetime.utcnow() - longest_period).fetch()
        logging.info("users: %s" % len(users))
        emails_sent = {
            0: [],
            1: [],
            6: [],
            9: [],
            14: []
        }
        for user in users:
            duration_joined = datetime.utcnow() - user.started
            email = user.email

            if duration_joined.days == 0:
                try:
                    logging.info("0 welcome %s" % email)
                    UserInfo.send_email(email, 'Welcome to zenblip!', 'welcome', sync=sync)
                    emails_sent[0].append(email)
                except Exception as e:
                    logging.error(e)
            elif duration_joined.days == 1:
                try:
                    logging.info("1 welcome_hint %s" % email)
                    UserInfo.send_email(
                        email,
                        'zenblip HINT: (I got a notification that says "Someone" opened an email)',
                        'welcome_hint',
                        sync=sync)
                    emails_sent[1].append(email)
                except Exception as e:
                    logging.error(e)
            elif duration_joined.days == 6:
                try:
                    logging.info("6 welcome_any_problems %s" % email)
                    UserInfo.send_email(email, 'Any problems?', 'welcome_any_problems', sync=sync)
                    emails_sent[6].append(email)
                except Exception as e:
                    logging.error(e)
            elif duration_joined.days == 9:
                try:
                    logging.info("9 welcome_tip %s" % email)
                    UserInfo.send_email(email, 'zenblip TIP: Forwarded emails', 'welcome_tip', sync=sync)
                    emails_sent[9].append(email)
                except Exception as e:
                    logging.error(e)
            elif duration_joined.days == 14:
                try:
                    logging.info("14 welcome_feedback %s" % email)
                    UserInfo.send_email(email, 'zenblip Comments & Feedback', 'welcome_feedback', sync=sync)
                    emails_sent[14].append(email)
                except Exception as e:
                    logging.error(e)

        logging.info(emails_sent)
        self.context['data'] = {'emails_sent': emails_sent}

    @route_with('/cron/send_test_scheduled_emails')
    def send_test_scheduled_emails(self):

        logging.info('send_test_scheduled_emails')
        self.meta.change_view('json')
        sync = self.request.get('sync', False)

        email = 'sushi@zenblip.com'
        UserInfo.send_email(email, 'Welcome to zenblip!', 'welcome', sync=sync)
        UserInfo.send_email(email, 'zenblip HINT: (I got a notification that says "Someone" opened an email)', 'welcome_hint', sync=sync)
        UserInfo.send_email(email, 'Any problems?', 'welcome_any_problems', sync=sync)
        UserInfo.send_email(email, 'zenblip TIP: Forwarded emails', 'welcome_tip', sync=sync)
        UserInfo.send_email(email, 'zenblip Comments & Feedback', 'welcome_feedback', sync=sync)
