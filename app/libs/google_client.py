# -*- coding: utf-8 -*-
'''
Created on 2015/4/12

@author: sushih-wen
'''

import re
import logging
import json
import urllib
from datetime import datetime
from google.appengine.api import users, urlfetch, memcache
from google.appengine.ext import deferred
from app.models.user_info import UserInfo
from app.models.device_client import DeviceClient
from app.utils import is_user_legit, is_email_valid
from libs.itsdangerous import JSONWebSignatureSerializer
from ferris import settings

class GoogleClient():

    """
    make use of appengine apis
    """

    def __init__(self, 
                 user_info, #UserInfo instance
                 client_id=settings.get('GOOGLE_CLIENT_ID'),
                 client_secret=settings.get('GOOGLE_CLIENT_SECRET')):
                     
        assert isinstance(user_info, UserInfo)
        
        self.client_id = client_id
        self.client_secret = client_secret
        
        assert user_info.google_id
        assert user_info.refresh_token
        
        self.user_id = user_info.google_id
        
        #set access token
        self.access_token = None
        self.obtain_new_access_token_from_refresh_token(user_info.refresh_token)

    def obtain_new_access_token_from_refresh_token(self, refresh_token):
        """
        return
        {
          "access_token":"1/fFBGRNJru1FQd44AzqT3Zg",
          "expires_in":3920,
          "token_type":"Bearer",
        }
        """
        assert refresh_token
        access_token = memcache.get("GoogleClientAccessToken::%s" % refresh_token)
        if access_token:
            self.access_token = access_token
            return access_token
            
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }

        payload = urllib.urlencode(payload)
        try:
            r = urlfetch.fetch("https://www.googleapis.com/oauth2/v3/token", payload=payload, method=urlfetch.POST)
        except:
            # simpe retry
            r = urlfetch.fetch("https://www.googleapis.com/oauth2/v3/token", payload=payload, method=urlfetch.POST)

        if r.status_code != 200:
            logging.error("obtain_new_access_token_from_refresh_token Error")
            logging.error(r.content)
            return None
        
        
        jdata = json.loads(r.content)
        access_token = jdata.get('access_token', None)
        if not access_token:
            return None
        self.access_token = access_token
        default_token_expires_in_seconds = 3600
        time_buffer_in_seconds = 30
        memcache.set("GoogleClientAccessToken::%s" % refresh_token, access_token, 
                     int(jdata.get('expires_in', default_token_expires_in_seconds)) - time_buffer_in_seconds)
        
        return access_token

    def get_resource(self, resource_uri):
        logging.info('access_token: %s' % self.access_token)
        if not self.access_token:
            return None
        if not self.access_token.startswith('Bearer '):
            access_token = 'Bearer ' + self.access_token
        try:
            result = urlfetch.fetch(resource_uri, method='GET', headers={'Authorization': access_token})
            return json.loads(result.content)
        except Exception as e:
            logging.exception(e)
            return {'error': str(e)}


class GoogleMessageClient(GoogleClient):

    def to_query_string(self, subject, tos=[], ccs=[], bccs=[], after=None):
        query_string=""
        if subject:
            try:
                subject = subject.encode('utf-8') #urlencode doesn't like unicode
                query_string += "subject:%s " % subject
            except:
                logging.exception(subject)
        if tos:
            try:
                for to in tos:
                    to = to.encode('utf-8')
                    query_string += "to:%s " % to
            except:
                logging.exception(tos)
        if ccs:
            try:
                for cc in ccs:
                    cc = cc.encode('utf-8')
                    query_string += "cc:%s " % cc
            except:
                logging.exception(tos)
        if bccs:
            try:
                for bcc in bccs:
                    bcc = bcc.encode('utf-8')
                    query_string += "bcc:%s " % bcc
            except:
                logging.exception(tos)

        if after:
            query_string += "after:%s" % datetime.strftime(after, '%Y/%m/%d')

        return query_string

    def search_threads(self, subject="", tos=[], ccs=[], bccs=[], limit=1, after=None):
        """
        parms:
        https://support.google.com/mail/answer/7190?hl=en
        
        return:
        {
          "nextPageToken": "04980553828346998384", 
          "resultSizeEstimate": 12, 
          "threads": [
            {
              "snippet": "", 
              "id": "14cab994b7e4148e", 
              "historyId": "3044106"
            }, 
            {
              "snippet": "", 
              "id": "14cab6b07de9b360", 
              "historyId": "3044055"
            }
          ]
        }
        """
        
        query_string = self.to_query_string(subject, tos, ccs, bccs, after)
        
        logging.info(query_string)
        query_string = urllib.urlencode(dict(q=query_string, maxResults=limit))
        uri = 'https://www.googleapis.com/gmail/v1/users/%s/threads?%s' % (self.user_id, query_string)
        logging.info(uri)
        jdata = self.get_resource(uri)
        return jdata
            
    def search_messages(self, subject="", tos=[], ccs=[], bccs=[], limit=1, after=None):
        """
        {
          "resultSizeEstimate": 3, 
          "messages": [
            {
              "id": "14cf96f0816634b0", 
              "threadId": "14ce1358610e3579"
            }, 
            {
              "id": "14cf90f457f5824f", 
              "threadId": "14cea0c016dead78"
            }, 
            {
              "id": "14cf7ee1c5d7068e", 
              "threadId": "14ced89300defc90"
            }
          ]
        }
        """
        
        query_string = self.to_query_string(subject, tos, ccs, bccs, after)
        
        logging.info(query_string)
        query_string = urllib.urlencode(dict(q=query_string, maxResults=limit))
        uri = 'https://www.googleapis.com/gmail/v1/users/%s/messages?%s' % (self.user_id, query_string)
        logging.info(uri)
        jdata = self.get_resource(uri)
        return jdata
        

    def get_messages_from_threads(self, threads):
        return threads.get('messages', [])

    def get_threads(self, thread_id):
        uri = 'https://www.googleapis.com/gmail/v1/users/%s/threads/%s' % (self.user_id, thread_id)
        jdata = self.get_resource(uri)
        return jdata

    def get_message_thread_id(self, message_id):
        jdata = self.get_message(message_id)
        if jdata:
            return jdata.get('threadId', None)
        else:
            return None

    def get_message(self, message_id):
        """
        get an email's message
        """
        uri = 'https://www.googleapis.com/gmail/v1/users/%s/messages/%s' % (self.user_id, message_id)
        jdata = self.get_resource(uri)
        return jdata
