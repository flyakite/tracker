'''
Created on 2014/8/5

@author: sushih-wen
'''
import logging
from ferris import BasicModel
from google.appengine.ext import ndb
from google.appengine.ext import deferred
from ferris.core import mail
# from app.utils import is_email_valid


class Setting(BasicModel):
    email = ndb.StringProperty()
    track_by_default = ndb.BooleanProperty(default=True)
    is_notify_by_email = ndb.BooleanProperty(default=True)
    is_notify_by_desktop = ndb.BooleanProperty(default=True)
    is_daily_report = ndb.BooleanProperty(default=True)
    is_weekly_report = ndb.BooleanProperty(default=True)
    
    @classmethod
    def create(cls,
               email,
               track_by_default=True,
               is_notify_by_email=True,
               is_notify_by_desktop=True,
               is_daily_report=True,
               is_weekly_report=True):
                   
        setting = cls(email=email,
                      track_by_default=track_by_default,
                        is_notify_by_email=is_notify_by_email,
                        is_notify_by_desktop=is_notify_by_desktop,
                        is_daily_report=is_daily_report,
                        is_weekly_report=is_weekly_report
                        )
        setting.put()
        return setting

    def to_dict_output(self, include=['track_by_default',
                                      'is_notify_by_email',
                                      'is_notify_by_desktop',
                                      'is_daily_report',
                                      'is_weekly_report',
                                      'created',
                                      'modified'], exclude=[]):
        return self.to_dict(include=include, exclude=exclude)