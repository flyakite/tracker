'''
Created on 2014/8/21

@author: sushih-wen
'''
import re
import logging
import json
import urllib
from datetime import datetime
from google.appengine.api import users, urlfetch
from google.appengine.ext import deferred
from ferris import Controller, route_with
from ferris.core import mail
from base import BaseController
from app.models.user_info import UserInfo
from app.models.device_client import DeviceClient
from app.utils import is_user_legit, is_email_valid
from libs.itsdangerous import JSONWebSignatureSerializer

logger = logging.getLogger('default')
PROJECT_SECRET = 'zenblip_secret'
PROJECT_SALT = 'zenblip_salt'

def encode_token(dict_object):
    s = JSONWebSignatureSerializer(PROJECT_SECRET, salt=PROJECT_SALT)
    dict_object.update(_created = str(datetime.utcnow()))
    return s.dumps(dict_object)
    
def decode_token(code):
    s = JSONWebSignatureSerializer(PROJECT_SECRET, salt=PROJECT_SALT)
    try:
        return s.loads(code)
    except:
        return None

class Auths(BaseController):

    
    @route_with('/auth/login')
    def login(self):
        return self.redirect(users.create_login_url())

    @route_with('/auth/check')
    def check(self):
        self.meta.change_view('json')

        self._enable_cors()

        user = users.get_current_user()
        if not users.get_current_user():
            self.context['data'] = {'error': 'Unauthorized',
                                    'login_url': users.create_login_url()
                                    }
            return
        else:
            self.context['data'] = {'user': user.user_id()}
            return

    @route_with('/auth/google')
    def auth_chrome(self):
        """
        TODO:
        We used email to identify user.
        But in Google APIs, Google suggest not to use email, as one email can represent different identities.
        
        TODO: how to test this handler?
        """
        self.meta.change_view('json')
        self._enable_cors()
        sync = self.request.get('sync')

        access_token = self.request.headers.get('Authorization')
        if not access_token:
            logging.warning('no access_token')
            return
        logging.info('access_token: %s' % access_token)
        google_user_info_url = 'https://www.googleapis.com/userinfo/v2/me'

        try:
            result = urlfetch.fetch(google_user_info_url, method='GET', headers={'Authorization': access_token})
        except Exception as e:
            logging.error(e)
            self.context['data'] = {'error': str(e)}
            return

        """
        {
            id: "115587419112044369619"
            email: "sushi@zenblip.com"
            verified_email: true
            name: "Shih-Wen Su"
            given_name: "Shih-Wen"
            family_name: "Su"
            link: https://plus.google.com/115587419112044369619
            picture: https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg
            gender: "male"
            locale: "en"
            hd: "zenblip.com"
        }
        """
        if result.status_code == 200:
            logging.info(result.content)
            user_from_plus = json.loads(result.content)

            user_info = UserInfo.find_by_properties(google_id=user_from_plus['id'])
            if not user_info:
                user_info = UserInfo.find_by_properties(email=user_from_plus['email'])
            if not user_info:
                orgs = ['daily', 'weekly', 'activity']
                if user_from_plus.get('hd'):
                    orgs.append(user_from_plus.get('hd'))
                UserInfo.create_user(
                    email=user_from_plus['email'],
                    name=user_from_plus.get('name'),
                    given_name=user_from_plus.get('given_name'),
                    family_name=user_from_plus.get('family_name'),
                    picture=user_from_plus.get('picture'),
                    gender=user_from_plus.get('gender'),
                    locale=user_from_plus.get('locale'),
                    orgs=orgs,
                    last_seen=datetime.utcnow(),
                    domain=user_from_plus['email'].split('@')[1].lower(),
                    google_id=user_from_plus['id']
                )
            else:
                hd = user_from_plus.get('hd')
                user_info.email = user_from_plus['email']
                user_info.domain = user_info.email.split('@')[1].lower()
                user_info.name = user_from_plus.get('name')
                user_info.given_name = user_from_plus.get('given_name')
                user_info.family_name = user_from_plus.get('family_name')
                user_info.picture = user_from_plus.get('picture')
                user_info.gender = user_from_plus.get('gender')
                user_info.locale = user_from_plus.get('locale')
                if hd and hd not in user_info.orgs:
                    user_info.orgs.append(hd)
                user_info.last_seen = datetime.utcnow()
                user_info.google_id = user_from_plus['id']
                user_info.put()

            self.context['data'] = {'success': 1, 
                                    'email': user_from_plus['email'],
                                    'access_token': encode_token({'email':user_from_plus['email']})}
            
            self.set_session_user(user_from_plus['email'])
            self.get_or_set_csrf_token()
            
        else:
            self.context['data'] = {'error': 'status_error: %s' % result.status_code}

    
    @route_with('/auth/user')
    def auth_user(self):
        """
        Check if current_user exist, return User_Info, deprecated, use auth_google
        """
        self.meta.change_view('json')
        self._enable_cors()
        user = self.current_user
        if user:
            self.context['data'] = {'email': user.email,
                                    'name': user.name,
                                    'orgs': user.orgs,
                                    'role': user.role,
                                    'access_token': encode_token({'email':user.email}),
                                    'tz_offset': user.tz_offset
                                    }
        else:
            self.context['data'] = {'error': True}
            
    @route_with('/auth/demo')
    def auth_demo(self):
        """
        Just a debug demo, this function can be removed
        """
        self.meta.change_view('json')
        self._enable_cors()
        user = self.current_user
        if user:
            self.context['data'] = {'email': user.email,
                                    'name': user.name,
                                    'orgs': user.orgs,
                                    'role': user.role,
                                    'tz_offset': user.tz_offset
                                    }
        else:
            self.context['data'] = {'error': True}
            
    @route_with('/auth/legit')
    def auth_legit(self):
        """
        check if a email is legit
        """
        logging.info('auth_legit')
        self.meta.change_view('json')
        self._enable_cors()
        email = self.request.get('email')
        result = is_user_legit(email)
        self.context['data'] = result
        return

    @route_with('/auth/activate_account')
    def auth_activate_account(self):
        """
        activate account for outlook user
        """
        self.meta.change_view('json')
        self._enable_cors()
        email = self.request.get('email')
        client_id = self.request.get('client_id')
        client_name = self.request.get('client_name')
        logging.info('email %s' % email)
        logging.info('client_id: %s' % client_id)
        logging.info('client_name: %s' % client_name)
        if email and is_email_valid(email) and client_id and len(client_id) > 20:
            dc = DeviceClient.find_by_properties(owner=email, client_id=client_id)
            if not dc:
                dc = DeviceClient(owner=email,
                                  client_id=client_id,
                                  client_name=client_name)
                dc.put()
            self.context['data'] = {'success': True,
                                    'error': '',
                                    'data': ''}
        else:
            logging.error('invalid_email_or_client_id')
            self.context['data'] = {'success': False,
                                    'error': 'invalid_email_or_client_id',
                                    'data': ''}

    @route_with('/auth/verify_client')
    def auth_verify_client(self):
        """
        activate account for outlook user
        """
        self.meta.change_view('json')
        self._enable_cors()
        client_id = self.request.get('client_id')
        client_name = self.request.get('client_name')
        logging.info('client_id: %s' % client_id)
        logging.info('client_name: %s' % client_name)

        if client_id:
            dcs = DeviceClient.query(DeviceClient.client_id == client_id).order(-DeviceClient.modified).fetch(1)
            if dcs:
                dc = dcs[0]
                logging.info('email: %s' % dc.owner)
                self.context['data'] = {'success': True,
                                        'error': '',
                                        'data': dc.owner}
            else:
                logging.error('device_client_not_found')
                self.context['data'] = {'success': False,
                                        'error': 'device_client_not_found',
                                        'data': ''}

        else:
            logging.error('invalid_client_id')
            self.context['data'] = {'success': False,
                                    'error': 'invalid_client_id',
                                    'data': ''}
                                    
    @route_with('/auth/access_token')
    def get_access_token(self):
        self.meta.change_view('json')
        callback = self.request.get('callback')
        check_permission_email = self.request.get('check_permission_email')
        
        data = {}
        if self.current_user():
            url = "http://console.zenblip.com/accounts/access_token"
            payload = {'user_email':self.current_user().email, 'check_permission_email':check_permission_email}
            payload = urllib.urlencode(payload)
            result = urlfetch.fetch(url=url)
            if result.status_code == 200:
                data = json.loads(result.content)
        else:
            data = {'error':True, 'signed_in': False}
            
        logging.info(data)
        
        if callback and re.match(r'^[\w\.-]+$', callback):
            """
            JSONP
            """
            self.response.content_type = "text/plain"
            self.response.write('%s(%s)' % (callback, json.dumps(data)))
        else:
            self.context['data'] = data
