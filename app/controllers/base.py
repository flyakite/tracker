'''
Created on 2014/8/21

@author: sushih-wen
'''
import logging
import webapp2
from uuid import uuid4
from google.appengine.api import users, urlfetch
from ferris import Controller, route_with, scaffold
from ferris.core.views import View
from app.models.user_info import UserInfo


class BaseController(Controller):
    # TODO: make it a decorator

    def _enable_cors(self, origin='*'):
        logging.info('cors enabled')
        self.response.headers.content_type = 'application/json'
        # TODO: need to improve '*'
        # check domain first and retrun '*'
        self.response.headers.add_header('Access-Control-Allow-Origin', origin)

    def _login_required(self, url='/'):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(url))
            return
        return user

    def _admin_required(self, url='/'):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(url))
            return
        if not users.is_current_user_admin():
            self.abort(403)
            return
        return user

    def set_session_user(self, email):
        self.session['user_email'] = email

    @webapp2.cached_property
    def current_user(self):
        user_email = self.session.get('user_email')
        if user_email:
            logging.info('current_user_email: %s' % user_email)
            return UserInfo.find_by_properties(email=user_email)
        else:
            return None

    def get_or_set_csrf_token(self):
        _csrf_token = self.request.cookies.get('_csrf_token')
        logging.info('_csrf_token: %s' % _csrf_token)
        if not _csrf_token:
            logging.info('create csrf_token')
            _csrf_token = str(uuid4())[:8]
            self.response.set_cookie('_csrf_token', _csrf_token, max_age=30 * 86400)
        return _csrf_token

    def csrf_token_valid(self):
        if self.request.method in ['POST', 'PUT'] \
                and self.csrf_token != self.request.get('_csrf_token'):
            return False
        return True


class BaseView(View):

    def render(self, *args, **kwargs):
        pass
