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
from app.models.setting import Setting
from app.utils import is_user_legit, is_email_valid
from auths import encode_token, decode_token

# class Plan(object):
#     DEFAULT = ''
#     FREE = 'FR'
#     PRO='PR'
#     TEAM='TE'
#
# PLAN_TO_ROLE = {
#                 Plan.DEFAULT: 1,
#                 Plan.FREE: 1,
#                 Plan.PRO: 2,
#                 Plan.TEAM: 3
#                 }


def _is_true(value):
    if value in ['True', 'true', '1', 'on']:
        return True
    else:
        return False


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
    # TODO: add error message
    #             self.context['data'] = {'success': False, 'error': ''}
    #         else:
    # TODO: add error message
    #             self.context['data'] = {'success': False, 'error': ''}
    # TODO: set response status_code 401
    #
    #     @route_with('/api/signals')
    #     def signals(self):
    #         self.meta.change_view('json')
    #         self._enable_cors()
    # TODO: put auth in decorator
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

    # deprecated, we dont update the subscription realtime

    #     @route_with('/subscription_user')
    #     def subscription_user(self):
    #         logging.info('here')
    #         self.meta.change_view('json')
    #         if self.request.method == 'POST':
    #             logging.info(self.request.POST)
    #             rsvp = self.request.get('rsvp')
    #             if rsvp:
    # single email rsvp
    #                 subid = self.request.get('subid')
    #                 email = self.request.get('email')
    #                 plan = self.request.get('plan')
    #
    #                 if not is_email_valid(email):
    #                     logging.error("InvalidEmail %s" % email)
    #                     self.context['data'] = {'error':True,
    #                                             'error_message': 'Email Invalid'}
    #                     return
    #
    #
    #
    #                 ui = UserInfo.find_by_properties(email=email)
    #                 if ui and subid not in ui.orgs:
    #                     ui.orgs.append(subid)
    #                     role = PLAN_TO_ROLE.get(plan, 0)
    #                     if role > ui.role:
    #                         ui.role = role
    #                     ui.put()
    #                     logging.info("UserInfoUpdated %s" % email)
    #                 else:
    #                     UserInfo.create_user(
    #                         email=email,
    #                         orgs=[subid],
    #                         role = PLAN_TO_ROLE.get(plan, 0),
    #                         domain=email.split('@')[1].lower()
    #                     ).put()
    #                     logging.info("UserInfoCreated %s" % email)
    #
    #             else:
    #                 subid = self.request.get('subid')
    #                 emails_to_remove = self.request.get('emails_to_remove')
    #                 emails_to_create = self.request.get('emails_to_create')
    #                 rui = UserInfo.query(UserInfo.email.IN(emails_to_remove)).fetch()
    #                 ui_to_update = []
    #                 for ui in rui:
    #                     if subid in ui.orgs:
    #                         s_orgs = set(ui.orgs)
    #                         s_orgs.remove(subid)
    #                         ui.orgs = list(s_orgs)
    #                         ui_to_update.append(ui)
    #
    #                 if ui_to_update:
    #                     ndb.put_multi(ui_to_update)
    #                     logging.info("UserInfoCreated %s" % [ui.email for ui in ui_to_update])
    #
    #         else:
    #             self.abort(403)

    # deprecated, we don't update reprot group in realtime, but get report info right before sending the report

    #     @route_with('/subscription_report_group')
    #     def subscription_report_group(self):
    #         self.meta.change_view('json')
    #         if self.request.method == 'POST':
    #             subid = self.request.get('subid')
    #             emails = self.request.get('emails')
    #             logging.info(self.request.POST)
    #
    #             new_emails = set(filter(is_email_valid, emails))
    #             rg = ReportGroup.find_by_properties(rgid=subid)
    #             if rg:
    #                 orig_emails = set(rg.to)
    #                 if orig_emails != new_emails:
    #                     rg.emails = list(new_emails)
    #                     rg.put()
    #                 else:
    #                     logging.info('emails are the same')
    #             else:
    #                 logging.info('create new report group')
    #                 ReportGroup(rgid=subid,
    #                             orgs = [subid],
    #                             emails = new_emails
    #                             ).put()
    #                 logging.info("ReportGroupCreated %s" % subid)
    #         else:
    #             self.abort(403)

    @route_with('/settings')
    def settings(self):
        self.meta.change_view('json')
        self._enable_cors()
        email = self.request.get('email')
        logging.info(email)
        if not is_email_valid(email):
            self.context['data'] = {'error_message': 'No Email',
                                    'error': 1}
            self.abort(404)
            return
        
        # TODO: create a decorator to verify access_token
        access_token = self.request.get('access_token')
        if not access_token:
            logging.error('No Access Token')
            return self.abort(403)
        if access_token not in ['temp', '1lk3j5hgl1k5g15ATHATH35523jkgETHWYqetrkj_THTHQ25hwTYH2556DHMETJM2452h25']:  # TODO: to be removed
            data = decode_token(access_token)
            logging.info(data)
            if not data or (data.get('user_plans') and email not in data.get('user_plans').keys()):
                logging.info(email)
                logging.error('Access Token Invalid')
                return self.abort(403)

        setting = Setting.find_by_properties(email=email)

        if self.request.method == 'GET':
            #from client side
            logging.info(self.request.GET.items())
            user_info = UserInfo.find_by_properties(email=email)
            if not setting:
                if user_info:
                    logging.info('CreateSetting')
                    setting = Setting.create(email=email)
                else:
                    logging.error('SettingNotFound')
                    self.context['data'] = {'error_message': 'SettingNotFound',
                                        'error': 1}
                return
            
            
            s = setting.to_dict_output()
            has_refresh_token = True if user_info and user_info.refresh_token else False
            s.update(dict(has_refresh_token=has_refresh_token))
            logging.info(s)
            self.context['data'] = s
            return
        elif self.request.method == 'POST':
            logging.info(self.request.POST.items())
            track_by_default = self.request.get('track_by_default')
            is_notify_by_email = self.request.get('is_notify_by_email')
            is_notify_by_desktop = self.request.get('is_notify_by_desktop')
            is_daily_report = self.request.get('is_daily_report')
            is_weekly_report = self.request.get('is_weekly_report')
            if not setting:
                setting = Setting.create(email=email)

            setting.track_by_default = True if _is_true(track_by_default) else False
            # if is_notify_by_email != None:
            setting.is_notify_by_email = True if _is_true(is_notify_by_email) else False
            # if is_notify_by_desktop != None:
            setting.is_notify_by_desktop = True if _is_true(is_notify_by_desktop) else False
            # if is_daily_report != None:
            setting.is_daily_report = True if _is_true(is_daily_report) else False
            # if is_weekly_report != None:
            setting.is_weekly_report = True if _is_true(is_weekly_report) else False

            setting.put()
            self.context['data'] = {'success': 1}
            return
        else:
            return self.abort(403)
