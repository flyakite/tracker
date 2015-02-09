'''
Created on 2014/12/25

@author: sushih-wen
'''

import logging
import json
from datetime import datetime
from google.appengine.api import users, urlfetch
from google.appengine.ext import deferred
from ferris import Controller, route_with
from ferris.core import mail
from base import BaseController
from app.models.api_key import ApiKey
from app.models.device_client import DeviceClient
from app.utils import is_user_legit, is_email_valid


class Apis(BaseController):

    @route_with('/api/auth')
    def auth(self):
        self.meta.change_view('json')
        self._enable_cors()

        if self.request.method == 'POST':
            token = ''
            access_id = self.request.get('access_id')
            secret = self.request.get('secret')
            if access_id and secret:
                if ApiKey.verify_secret(access_id, secret):
                    token = ApiKey.create_token(access_id, secret)
                    self.context['data'] = {'success': True, 'token': token}
                    return
            # TODO: add error message
            self.context['data'] = {'success': False, 'error': ''}
        else:
            # TODO: add error message
            self.context['data'] = {'success': False, 'error': ''}
            # TODO: set response status_code 401

    @route_with('/api/signals')
    def signals(self):
        self.meta.change_view('json')
        self._enable_cors()
        # TODO: put auth in decorator
        access_id = self.request.headers.get('X-Access-ID', '')
        token = self.request.headers.get('X-User-Token', '')
        if not access_id:
            logging.error('no_access_id')
            self.context['data'] = {'success': False, 'error': 'no_access_id'}
            return
        elif not token:
            logging.error('no_token')
            self.context['data'] = {'success': False, 'error': 'no_token'}
            return
        elif not ApiKey.verify_token(access_id, token):
            logging.error('token_verification_failed')
            self.context['data'] = {'success': False, 'error': 'token_verification_failed'}
            return

        sender = self.request.get('sender')
