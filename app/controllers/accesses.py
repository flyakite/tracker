'''
Created on 2014/8/23

@author: sushih-wen
'''

import json
import re
import random
import logging
import cPickle as pickle
from datetime import datetime, timedelta
from uuid import uuid4
from urllib import urlencode
from google.appengine.api import memcache, urlfetch, channel, taskqueue
from google.appengine.ext import deferred, ndb
from ferris import route_with
from ferris.core import mail
from app.models.link import Link
from app.models.access import Access
from app.models.signal import Signal
from app.models.user_track import UserTrack
from app.models.channel_client import ChannelClient
from app.models.setting import Setting
from base import BaseController
from ferris import settings


class SourceInfo(object):

    def __init__(self, ip=None, country=None, city=None, tz_offset=None, proxy=None, device=None):
        self.ip = ip
        self.country = country
        self.city = city
        self.tz_offset = tz_offset
        self.proxy = proxy
        self.device = device


class AccessNotification(object):

    """
    """

    def __init__(self, signal, access, kind=None, message='', recent_accesses=None):
        self.kind = kind
        self.message = ''
        self.signal = signal
        self.access = access
        self.recent_accesses = recent_accesses
        if signal.notification_setting in ['e', '', None]:
            self.is_sending_email_notification = True
        else:
            self.is_sending_email_notification = False
        if signal.notification_setting in ['d', '', None]:
            self.is_sending_desktop_notification = True
        else:
            self.is_sending_desktop_notification = False

    @staticmethod
    def kinds():
        return ['first_access', 'high_frequent', 'second_access', 'delay_notify']


class Accesses(BaseController):

    @route_with('/tasks/delayed_access_notification')
    def tasks_delayed_access_notification(self):
        self.meta.change_view('json')

        sync = self.request.get('sync')
        token = self.request.get('token')
        access_id = str(self.request.get('access_id'))
        signal = Signal.find_by_properties(token=token)
        access = Access.get_by_id(access_id, signal.key)
        accesses = Access.query(ancestor=signal.key).filter(Access.created >= signal.notify_triggered).order(-Access.created).fetch()
        if not accesses:
            logging.warning('no accesses')
            return

        recent_accesses = []
        accesses.reverse()
        for a in accesses:
            recent_accesses.append(a)

        an = AccessNotification(signal=signal,
                                access=access,
                                recent_accesses=recent_accesses)

        an.kind = 'delay_notify'

        signal.notify_triggered = None
        signal.put()

        args = [signal.sender, signal.subject]
        kwargs = dict(template_name='access_notification',
                      context={'signal': signal,
                               'an': an,
                               'signal_code': Signal.encode_signal_token(signal.token),
                               'timedelta': timedelta})

        if sync:
            mail.send_template(*args, **kwargs)
        else:
            # Pickling of datastore_query.PropertyOrder is unsupported.
            deferred.defer(mail.send_template, *args, **kwargs)

    def _ensure_my_ass(self, my_email, sync):
        """
        create self access token, to prevent self trigger the signal
        """
        ass = self.request.cookies.get('ass')
        if ass:
            ut = UserTrack.find_by_properties(ass=ass)
            if my_email not in ut.emails:
                ut.emails.append(my_email)
            ut.put() if sync else ut.put_async()
        else:
            ut = UserTrack.find_by_properties(emails=my_email)
            if ut:
                self.response.set_cookie('ass', ut.ass)
            else:
                new_ass = UserTrack.new_ass()
                ut = UserTrack(
                    ass=new_ass,
                    emails=[my_email]
                )
                ut.put() if sync else ut.put_async()

    def _recognize_user(self, signal, sync):
        """
        recognize user
        save track to db and cookie for later recognize

        return accessor and ass(cookie)
        """
        # record access, who accessed?
        # TODO: improve receiver recognition

        ass = self.request.cookies.get('ass')

        receivers = signal.receivers

        accessor = {}

        logging.info('receipant_count: %s' % receivers.get('c', ''))
        if receivers['c'] == 1:
            for k in Signal.receiver_keys():
                if receivers[k]:
                    accessor = receivers[k]
                    break

            if self._get_source_proxy() is not None:
                logging.info('access_from_procxy')
                # access from proxy(Google proxy), make a guess
                return accessor, ass

            if not accessor:
                # some error when creating the receivers, the sum is incorrect
                logging.error("some error when creating the receivers, the sum is incorrect")
                return None, ass

            if ass:
                # the user has accessed before
                logging.info('the user accessed before, the ass cookie: %s' % ass)
                user_track = UserTrack.find_by_properties(ass=ass)

                # prevent self access
                if user_track and signal.sender in user_track.emails:
                    accessor.update({signal.sender: ''})
                    return accessor, ass

                # update user email of this ass
                if user_track and accessor.keys()[0] not in user_track.emails:
                    user_track.emails.append(accessor.keys()[0])
                    user_track.put() if sync else user_track.put_async()
                return accessor, ass
            else:
                user_tracks = UserTrack.find_all_by_properties(emails=accessor.keys()[0]).order(UserTrack.created).fetch(10)
                if len(user_tracks) > 1:
                    try:
                        logging.warning("same email in different user_tracks: %s len: %s" % (accessor.keys()[0], len(user_tracks)))
                    except:
                        pass

                new_ass = None
                if user_tracks:
                    # use the earliest created user_track
                    logging.info('no ass cookie but we have record of this email: %s' % accessor.keys()[0])
                    user_track = user_tracks[0]
                    # maybe request comes from a proxy, or diferent devices
                    new_ass = user_track.ass
                    logging.info('no ass record of this email: %s' % ass)
                else:
                    # maybe a new commer
                    logging.info('create new ass cookie')
                    new_ass = UserTrack.new_ass()
                    user_track = UserTrack(ass=new_ass, emails=[accessor.keys()[0]])
                    user_track.put() if sync else user_track.put_async()

                if new_ass:
                    self.response.set_cookie('ass', new_ass)
                return accessor, new_ass

        else:
            return None, ass

    def _get_source_proxy(self):
        proxy = None
        remote_addr = self.request.remote_addr
        logging.info('_get_source_proxy %s' % remote_addr)
        if remote_addr:
            try:
                ip_secs = remote_addr.split('.')
                # https://ipdb.at/org/Microsoft_Hosting
                if ip_secs[0] == '65':
                    if ip_secs[1] in ['52', '53', '54', '55']:
                        proxy = 'MicrosoftHosting'
                elif ip_secs[0] == '70':
                    if ip_secs[1] == '37':
                        proxy = 'MicrosoftHosting'
            except Exception as ex:
                logging.error(ex)
                pass

        user_agent = self.request.headers.get('User-Agent', '')
        if 'GoogleImageProxy' in user_agent:
            proxy = 'GoogleImageProxy'

        return proxy

    def _get_source_info(self):

        source = SourceInfo()

        proxy = self._get_source_proxy()
        logging.info('_get_source_info proxy: %s' % proxy)
        if proxy:
            source.proxy = proxy
            if proxy == 'GoogleImageProxy':
                source.device = 'Gmail client'
                return source
            elif proxy == 'MicrosoftHosting':
                source.device = 'Microsoft Outlook'
                return source

        source = self._get_ip_info(source=source)
        user_agent = self.request.headers.get('User-Agent', '')
        if source and user_agent:
            source.device = self._user_agent_to_device(user_agent)

        return source

    def _user_agent_to_device(self, user_agent=''):
        if 'iPhone' in user_agent:
            return 'iPhone'
        elif 'iPod' in user_agent:
            return 'iPod'
        elif 'iPad' in user_agent:
            return 'iPad'
        elif 'Android' in user_agent:
            return 'Android'
        elif 'BlackBerry' in user_agent:
            return 'BlackBerry'
        elif 'IEMobile' in user_agent:
            return 'Windows Phone'
        elif 'Kindle' in user_agent:
            return 'Kindle'
        elif re.search(r'Mobile|NetFront|Silk-Accelerated|(hpw|web)OS|Fennec|Minimo|Opera M(obi|ini)|Blazer|Dolfin|Dolphin|Skyfire|Zune', user_agent):
            return 'mobile device'
        elif 'Macintosh' in user_agent:
            return 'Macintosh'
        elif 'Linux' in user_agent:
            return 'Linux'
        elif 'Microsoft Outlook' in user_agent:
            return 'Microsoft Outlook'
        elif 'Windows' in user_agent:
            return 'Windows'
        else:
            return None

    def _get_ip_info(self, source=SourceInfo(), ipaddress=None, ):

        if not ipaddress and self.request and not self.request.remote_addr:
            logging.error("no remote_addr")
            return None

        source.ip = ipaddress or self.request.remote_addr

        # get from memcache
        mem_ip_info = memcache.get(source.ip)
        if mem_ip_info:
            logging.info('found ip_info in memcache')
            source.country = mem_ip_info.get('country', None)
            source.city = mem_ip_info.get('stateprov', None)
            try:
                source.tz_offset = int(mem_ip_info.get('tz_offset', None))
            except:
                source.tz_offset = None
            return source

        rpc = urlfetch.create_rpc()
        args = {
            'addr': source.ip,
            'api_key': random.choice(settings.get('db_ip_api_keys'))
        }
        url_args = urlencode(args)

        try:
            urlfetch.make_fetch_call(rpc, settings.get('db_ip_base_url') + '?' + url_args)
            result = rpc.get_result()
            logging.debug('result.status_code: %s' % result.status_code)
            logging.debug('result.content: %s' % result.content)
            if result.status_code == 200:
                try:
                    j = json.loads(result.content)
                    """
                       {
                        address: "68.4.112.174"
                        country: "US"
                        stateprov: "California"
                        city: "Irvine"
                        }
                    """
                    # TODO: deal with insufficient api quota (queries_left)
                    if 'error' in j:
                        logging.error("db_ip returns error" % result.content)
                        return None

                    memcache.set(source.ip, j)

                    source.country = j.get('country', None)
                    # city is not accurate at current moment
                    #source.city = j.get('city', None)
                    source.city = j.get('stateprov', None)
                    try:
                        source.tz_offset = int(j.get('tz_offset', None))
                    except:
                        source.tz_offset = None
                    return source

                except Exception as e:
                    logging.error("db_ip exception: %s" % result.content)
                    return None
            else:
                logging.error("db_ip status not 200: %s %s" % (result.status_code, result.content))
                return None

        except urlfetch.DownloadError as e:
            logging.error("db_ip fetch DownloadError")
            logging.error(e)
            return None

    def _check_notify_time_threshold(self, an, signal):
        """
        we don't want to bomb the users, so after first 1 and 2 access, there's time threshold to send emails
        """
        if signal.notify_triggered and datetime.utcnow() - signal.notify_triggered < timedelta(minutes=60):
            an.is_sending_email_notification = False
            an.is_sending_desktop_notification = False
            an.kind = 'within_time_threshold'
        return an

    def _match_notify_criteria(self, signal, access):
        """
        We don't notify the user about every access, only the important onces
        1. first access
        2. frequent access
        3. second access
        """
        _recent_access_time_period_in_minutes = 60
        _recent_access_threshold = 3

        logging.info('signal.tz_offset %s' % signal.tz_offset)
        logging.info(access.created)

        logging.info('signal.notification_setting: %s' % signal.notification_setting)

        an = AccessNotification(signal, access)

        if not an.is_sending_email_notification:
            an.kind = 'is_not_sending_email_notification'
            return an

        accesses = Access.query(ancestor=signal.key).order(-Access.created).fetch()
        if not accesses:
            logging.warning('no accesses, first access')
            an.kind = 'first_access'
            return an

        kinds = {}
        recent_accesses = []
        accesses.reverse()
        for a in accesses:
            if a.kind not in kinds:
                if a.key == access.key:
                    an.kind = 'first_access'
                    an.access.created = an.access.created
                    return an
                else:
                    kinds[a.kind] = 1

            elif kinds[a.kind] == 1 and a.key == access.key:
                # second_access
                an.kind = 'second_access'
                an.access.created = an.access.created
                return an
            else:
                kinds[a.kind] += 1

            # calculate frquency
#             if access.created - a.created < timedelta(minutes=_recent_access_time_period_in_minutes):
#                 recent_accesses.append(a)

        # we don't want to bomb the users, so after first 1 and 2 access, there's time threshold to send emails
        #an = self._check_notify_time_threshold(an, signal)

        # not first, not second, use delay
        an.is_sending_email_notification = False
        an.is_sending_desktop_notification = False
        if signal.notify_triggered:
            an.kind = 'notify_already_triggered'
            return an
        else:
            an.kind = 'delay_notify'
            return an

#         if recent_accesses and len(recent_accesses) > _recent_access_threshold:
#             an.kind = 'high_frequent'
#             an.recent_accesses = recent_accesses
#             return an

        return an

    def _notify_sender(self, signal, access, sync=False):
        """
        send notification to sender
        """

        access_notification = self._match_notify_criteria(signal, access)

        if access_notification.kind:
            logging.info('kind: %s' % access_notification.kind)
        else:
            logging.info('no access_notification.kind')

        setting = Setting.find_by_properties(email=signal.sender)
        if not setting:
            setting = Setting.create(signal.sender)
            
        if setting.is_notify_by_email:
            if access_notification.kind == 'delay_notify':
                """
                We can't use QueueStatistics because queuename is fixed in queue.yaml and task name can't be queried
                """
                signal.notify_triggered = access.created
                signal.put()  # TODO: check if it's dangerous to save here
    
                taskqueue.add(
                    url='/tasks/delayed_access_notification',
                    method='POST',
                    countdown=3600,  # seconds
                    params={'token': signal.token,
                            'access_id': str(access.key.id())}
                )
                logging.info('taskqueue added')
                return
    
            if access_notification.is_sending_email_notification and access_notification.kind in AccessNotification.kinds():
                self._send_email_message(access_notification, sync=sync)
                
        if setting.is_notify_by_desktop:
            if access_notification.is_sending_desktop_notification:
                self._send_channel_message(access_notification, sync=sync)

    def _send_email_message(self, access_notification, sync=False):
        signal = access_notification.signal
        access = access_notification.access
        logging.info(access.created)
        args = [signal.sender, signal.subject]
        # sender settings in settings.py
        kwargs = dict(template_name='access_notification',
                      context={'signal': signal,
                               'a': access,
                               'an': access_notification,
                               'signal_code': Signal.encode_signal_token(signal.token),
                               'timedelta': timedelta})

        if sync:
            mail.send_template(*args, **kwargs)
        else:
            # Pickling of datastore_query.PropertyOrder is unsupported.
            deferred.defer(mail.send_template, *args, **kwargs)

    def _send_channel_message(self, access_notification, sync=False):
        signal = access_notification.signal
        access = access_notification.access
        kind = access_notification.kind
        logging.info('send channel message %s %s' % (signal.token, signal.sender))
        cclient = ChannelClient.find_by_properties(owner=signal.sender)
        if cclient:
            logging.info('channel client: %s' % cclient.client_id)
            channel.send_message(cclient.client_id, json.dumps({'signal': signal.to_dict_output(),
                                                                'access': access.to_dict_output(),
                                                                'kind': kind}))
        else:
            logging.info('client not found %s' % signal.sender)

        """
        <div>
            {{a.accessor_name or a.accessor or "Someone"}}
            {% if a.kind == 'open' %} opened this email{% elif a.kind == 'link'%} accessed {{a.url}}{% else %}{% endif %}
            at {% if signal.tz_offset != None %}{{a.created.strftime('%H:%M:%S')}}{% else %}{{a.created.strftime('%H:%M:%S')}} UTC{% endif %}
            {% if a.country %}
                in {% if a.city %} {{a.city}}{% endif %}, {{a.country}}
            {% elif a.proxy == 'GoogleImageProxy'%}
                from Gmail client.
            {% endif %}<br /><br />
            </div>
        """
