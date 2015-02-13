'''
Created on 2014/12/25

@author: sushih-wen
'''

import logging
import json
from datetime import datetime
from google.appengine.api import users, urlfetch
from google.appengine.ext import deferred, ndb
from ferris import Controller, route_with
from ferris.core import mail
from base import BaseController
from app.models.api_key import ApiKey
from app.models.device_client import DeviceClient
from app.models.report_group import ReportGroup
from app.models.user_info import UserInfo
from app.utils import is_user_legit, is_email_valid


class Plan(object):
    DEFAULT = ''
    FREE = 'FR'
    PRO='PR'
    TEAM='TE'
    
PLAN_TO_ROLE = {
                Plan.DEFAULT: 1,
                Plan.FREE: 1,
                Plan.PRO: 2,
                Plan.TEAM: 3
                }

class Apis(BaseController):

#     @route_with('/api/auth')
#     def auth(self):
#         self.meta.change_view('json')
#         self._enable_cors()
# 
#         if self.request.method == 'POST':
#             token = ''
#             access_id = self.request.get('access_id')
#             secret = self.request.get('secret')
#             if access_id and secret:
#                 if ApiKey.verify_secret(access_id, secret):
#                     token = ApiKey.create_token(access_id, secret)
#                     self.context['data'] = {'success': True, 'token': token}
#                     return
#             # TODO: add error message
#             self.context['data'] = {'success': False, 'error': ''}
#         else:
#             # TODO: add error message
#             self.context['data'] = {'success': False, 'error': ''}
#             # TODO: set response status_code 401
# 
#     @route_with('/api/signals')
#     def signals(self):
#         self.meta.change_view('json')
#         self._enable_cors()
#         # TODO: put auth in decorator
#         access_id = self.request.headers.get('X-Access-ID', '')
#         token = self.request.headers.get('X-User-Token', '')
#         if not access_id:
#             logging.error('no_access_id')
#             self.context['data'] = {'success': False, 'error': 'no_access_id'}
#             return
#         elif not token:
#             logging.error('no_token')
#             self.context['data'] = {'success': False, 'error': 'no_token'}
#             return
#         elif not ApiKey.verify_token(access_id, token):
#             logging.error('token_verification_failed')
#             self.context['data'] = {'success': False, 'error': 'token_verification_failed'}
#             return
# 
#         sender = self.request.get('sender')
        
    @route_with('/subscription_user')
    def subscription_user(self):
        self.meta.change_view('json')
        if self.request.method == 'POST':
            logging.info(self.request.POST)
            rsvp = self.request.POST.get('rsvp')
            if rsvp:
                #single email rsvp
                subid = self.request.POST.get('subid')
                email = self.request.POST.get('email')
                plan = self.request.POST.get('plan')
                
                if not is_email_valid(email):
                    logging.error("InvalidEmail %s" % email)
                    self.context['data'] = {'error':True, 
                                            'error_message': 'Email Invalid'}
                    return
                
                
                
                ui = UserInfo.find_by_properties(email=email)
                if ui and subid not in ui.orgs:
                    ui.orgs.append(subid)
                    role = PLAN_TO_ROLE.get(plan, 0)
                    if role > ui.role:
                        ui.role = role
                    ui.put()
                    logging.info("UserInfoUpdated %s" % email)
                else:
                    UserInfo.create_user(
                        email=email,
                        orgs=[subid],
                        role = PLAN_TO_ROLE.get(plan, 0),
                        domain=email.split('@')[1].lower()
                    ).put()
                    logging.info("UserInfoCreated %s" % email)
                    
            else:
                subid = self.request.POST.get('subid')
                emails_to_remove = self.request.POST.get('emails_to_remove')
                emails_to_create = self.request.POST.get('emails_to_create')
                rui = UserInfo.query(UserInfo.email.IN(emails_to_remove)).fetch()
                ui_to_update = []
                for ui in rui:
                    if subid in ui.orgs:
                        s_orgs = set(ui.orgs)
                        s_orgs.remove(subid)
                        ui.orgs = list(s_orgs)
                        ui_to_update.append(ui)
            
                if ui_to_update:
                    ndb.put_multi(ui_to_update)
                    logging.info("UserInfoCreated %s" % [ui.email for ui in ui_to_update])
            
        else:
            self.abort(403)
            
        
        
    @route_with('/subscription_report_group')
    def subscription_report_group(self):
        self.meta.change_view('json')
        if self.request.method == 'POST':
            subid = self.request.POST.get('subid')
            emails = self.request.POST.get('emails')
            logging.info(self.request.POST)
            
            new_emails = set(filter(is_email_valid, emails))
            rg = ReportGroup.find_by_properties(rgid=subid)
            if rg:
                orig_emails = set(rg.to)
                if orig_emails != new_emails:
                    rg.emails = list(new_emails)
                    rg.put()
                else:
                    logging.info('emails are the same')
            else:
                logging.info('create new report group')
                ReportGroup(rgid=subid,
                            orgs = [subid],
                            emails = new_emails
                            ).put()
                logging.info("ReportGroupCreated %s" % subid)
        else:
            self.abort(403)
            
        
