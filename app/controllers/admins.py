# -*- coding: utf-8 -*-
'''
Created on 2014/10/8

@author: sushih-wen
'''

import json
import re
import logging
import cPickle as pickle
import base64
import zlib
from datetime import datetime, timedelta
from uuid import uuid4
from urllib import urlencode
from google.appengine.api import users, urlfetch, users, taskqueue
from google.appengine.ext import deferred, ndb
from ferris import Controller, route_with, scaffold
from ferris.core.auth import require_admin
from app.models.signal import Signal
from app.models.access import Access
from app.models.user_info import UserInfo
from app.models.channel_client import ChannelClient
from app.models.link import Link
from accesses import Accesses
from base import BaseController


class TempUser():

    def __init__(self, email, is_connected=False, orgs=[], last_seen=None, created=datetime.utcnow(), legit=False):
        self.email = email
        self.is_connected = is_connected
        self.orgs = orgs
        self.legit = legit
        self.last_seen = last_seen
        self.created = created


class Admins(BaseController):

    @route_with('/admin/user_list')
    def user_list(self):
        self._admin_required('/admin/user_list')

        org = self.request.get('org')
        legacy = self.request.get('legacy', False)
        active = self.request.get('active', False)
        
        if active:
            active_start = datetime.utcnow() - timedelta(days=60)
        else:
            active_start = datetime(1, 1, 1) #in case active_start is not defined
            
        users = []
        emails = []

        if legacy:
            # list all recent users
            # based on UserInfo and ChannelClient
            if active:
                ccs = ChannelClient.query(ChannelClient.modified > active_start).order(-ChannelClient.modified).fetch(500)
            else:
                ccs = ChannelClient.query().order(-ChannelClient.created).fetch(500)
                
            logging.info('channelclients: %s' % len(ccs))
            emails = [cc.owner for cc in ccs]
            is_connected = {cc.owner: {'last_seen': cc.modified} for cc in ccs}
            userinfos = UserInfo.query().fetch()
            logging.info('userinfos: %s' % len(userinfos))
            user_dict = {u.email: {'created': u.created} for u in userinfos}
            emails.extend([cc.owner for cc in ccs])
            emails = list(set(emails))
            user_orgs = {u.email: {'orgs': u.orgs} for u in userinfos}

            for e in emails:
                user = TempUser(e,
                                orgs=user_orgs.get(e, {'orgs': None})['orgs'],
                                is_connected=True if is_connected .get(e) else False,
                                last_seen=is_connected .get(e, {'last_seen': None})['last_seen'],
                                created=user_dict.get(e, {}).get('created')
                                )
                users.append(user)
        else:
            # based on UserInfo
            if org:
                #org is deprecated
                userinfos = UserInfo.query(UserInfo.orgs == org).fetch(500)
                userinfos.sort(key=lambda x: x.created, reverse=True)
            else:
                if active:
                    userinfos = UserInfo.query(UserInfo.modified > active_start).order(-UserInfo.modified).fetch(500)
                else:
                    userinfos = UserInfo.query().order(-UserInfo.created).fetch(500)
            logging.info('userinfos: %s' % len(userinfos))
            emails = [u.email for u in userinfos]
            ccs = ChannelClient.query(ChannelClient.owner.IN(emails)).fetch()
            logging.info('channelclients: %s' % len(ccs))
            user_connected = {cc.owner: {'last_seen': cc.modified} for cc in ccs}
            for u in userinfos:
                user = TempUser(u.email,
                                is_connected=True if user_connected.get(u.email) else False,
                                last_seen=user_connected.get(u.email, {'last_seen': None})['last_seen'],
                                orgs=u.orgs,
                                legit=u.role,
                                created=u.created
                                )
                users.append(user)

        self.context.update({'users': users,
                             'emails': emails})

    @route_with('/admin/remove_dul_signals')
    def remove_dul_signals(self):
        logging.info('remove_dul_signals')
        self.meta.change_view('json')
        self._admin_required('/admin/user_list')

        userinfos = UserInfo.query().fetch()
        logging.info(len(userinfos))
        emails = []
        count = 0
        for u in userinfos:
            sender = u.email
            emails.append(sender)
            count += 1
            taskqueue.add(url='/admin/remove_dul_signals_personal',
                          params={
                              'sender': sender
                          },
                          countdown=count * 10)
        self.context['data'] = {'emails': emails}

    @route_with('/admin/remove_dul_signals_personal')
    def remove_dul_signals_personal(self):
        logging.info('remove_dul_signals_personal 3')
        self.meta.change_view('json')
        sender = self.request.get('sender')
        logging.info(sender)
        start = datetime.utcnow() - timedelta(hours=48)
        end = datetime.utcnow() - timedelta(hours=40)
        signals = Signal.query(Signal.sender == sender, Signal.created > start, Signal.created < end) \
                        .order(Signal.created) \
                        .fetch()
        signals_by_token = {}
        for s in signals:
            if s.token not in signals_by_token:
                signals_by_token[s.token] = [s]
            else:
                signals_by_token[s.token].append(s)

        duls = {}
        for token, signals in signals_by_token.items():
            if len(signals) > 1:
                duls[token] = len(signals)
                logging.info('signal:%s len:%s' % (token, len(signals)))
                access_count = 0
                for s in signals:
                    if s.access_count > 0:
                        logging.info(s.access_count)
                        access_count += s.access_count
                logging.info('access_count sum %s' % access_count)
                first_signal, other_signals = signals[0], signals[1:]
                logging.info('first_signal %s' % first_signal.created)
                if access_count > 0:
                    first_signal.access_count = access_count
                    first_signal.put()

                keys_to_delete = [s.key for s in other_signals]
                logging.info('keys_to_delete %s %s' % (token, len(keys_to_delete)))
                ndb.delete_multi(keys_to_delete)

        self.context['data'] = {'duls': duls}

    @route_with('/admin/fix_user_started')
    def fix_user_started(self):
        """
        input POST emails
        update user's started property
        """
        logging.info('fix_user_started')
        self.meta.change_view('json')
        emails = self.request.get('emails')
        emails = emails.split(',')
        emails = [e.strip() for e in emails]
        logging.info(emails)
        userinfos = UserInfo.query(UserInfo.email.IN(emails)).fetch()
#         userinfos = UserInfo.query().fetch()
        logging.info(len(userinfos))
        users_to_put = []
        for user in userinfos:
            if not user.started:
                logging.info(user.email)
                user.started = user.created
                users_to_put.append(user)
#             if not user.domain:
#                 logging.info(user.email)
#                 user.domain = user.email.split('@')[1].lower()
#                 users_to_put.append(user)
#             if user.role != 1:
#                 logging.info(user.email)
#                 user.role = 1
#                 users_to_put.append(user)

        if users_to_put:
            ndb.put_multi(users_to_put)

        self.context['data'] = {'len': len(userinfos), 'put': len(users_to_put), }

    @route_with('/admin/legit_user')
    def legit_user(self):
        """
        input POST emails, orgs
        update or create user's role property to 1(to be legit)
        """
        logging.info('legit_user')
        self.meta.change_view('json')
        emails = self.request.get('emails', [])
        if emails:
            emails = emails.split(',')
            emails = [e.strip() for e in emails]
        logging.info(emails)
        orgs = self.request.get('orgs', [])
        if orgs:
            orgs = orgs.split(',')
            orgs = [str(org.strip()) for org in orgs]
        logging.info(orgs)
        add_orgs = self.request.get('add_orgs')

        users_to_put = []
        for email in emails:
            user = UserInfo.find_by_properties(email=email)
            if user:
                user.role = 1
                if orgs:
                    if add_orgs:
                        user.orgs.extend(orgs)
                    else:
                        user.orgs = orgs
            else:
                user = UserInfo(
                    email=email,
                    domain=email.split('@')[1].lower(),
                    role=1
                )
                if orgs:
                    user.orgs = orgs
            users_to_put.append(user)

        if users_to_put:
            ndb.put_multi(users_to_put)

        self.context['data'] = {'len': len(emails), 'put': len(users_to_put), }
