# -*- coding: utf-8 -*-
'''
Created on 2015/4/23

@author: sushih-wen
'''

import logging
from uuid import uuid4
from ferris import route_with
from base import BaseController
from app.models.templar import Templar
from auths import encode_token, decode_token

class Templars(BaseController):
    
    def check_access_token(self):
        # TODO: create a decorator to verify access_token
        
        owner = self.request.get('owner')
        logging.info('owner %s' % owner)
        if not owner:
            logging.error('no owner')
            return self.abort(403)
            
        access_token = self.request.get('access_token')
        if not access_token:
            logging.error('No Access Token')
            return self.abort(403)
            
        if access_token == 'test' and not self.request.remote_addr:
            return
            
        data = decode_token(access_token)
        logging.info(data)
        if not data or (data.get('user_plans') and owner not in data.get('user_plans').keys()):
            logging.error('Access Token Invalid')
            return self.abort(403)
    
    @route_with('/resource/templars')
    def list_templars(self):
        self.meta.change_view('json')
        self._enable_cors()
        self.check_access_token()
        owner = self.request.get('owner')
        templars = Templar.query(Templar.owner == owner, Templar.is_active == True).fetch(100)
        self.context['data'] = dict(data=[t.to_dict(
            include=['tid', 'owner', 'subject', 'body', 'used_times', 'replied_times',
                     'opened_times', 'created']) for t in templars])
                     
    @route_with('/resource/templar')
    def templar(self):
        self.meta.change_view('json')
        self._enable_cors()
        self.check_access_token()
        owner = self.request.get('owner')
        action = self.request.get('action')
        logging.info('action %s' % action)
        NUMBER_NO_STATISTIC_MEANING = 20
        
        if action in ['delete']:
            tid = self.request.get('tid')
            logging.info('tid %s' % tid)
            if not tid:
                logging.info('No tid')
                return
            if tid.startswith('test'):
                logging.info('test templar')
                return
                
            templar = Templar.find_by_properties(tid=tid)
            if templar and templar.owner == owner and templar.is_active:
                if templar.used_times <= NUMBER_NO_STATISTIC_MEANING:
                    templar.key.delete()
                else:
                    templar.is_active = False
                    templar.put()
                self.context['data'] = dict(success=1)
                    
        elif action in ['create']:
            tid = uuid4().hex
            if not Templar.find_by_properties(tid=tid):
                templar = Templar(
                    tid=tid,
                    subject=self.request.get('subject'),
                    body=self.request.get('body'),
                    owner=owner)
                templar.put()
                self.context['data'] = templar.to_dict(
                        include=['tid', 'owner', 'subject', 'body', 'used_times', 'replied_times',
                                 'opened_times', 'created']
                    )
                     
                     
                     
                     
                     
                     
                     