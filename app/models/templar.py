'''
Created on 2015/4/23

@author: sushih-wen
'''
import logging
from ferris import BasicModel
from google.appengine.ext import ndb
from google.appengine.ext import deferred
from ferris.core import mail
#from app.utils import is_email_valid


class Templar(BasicModel):
    tid = ndb.StringProperty()
    subject = ndb.StringProperty()
    body = ndb.StringProperty()
    owner = ndb.StringProperty()
    used_times = ndb.IntegerProperty(default=0)
    replied_times = ndb.IntegerProperty(default=0)
    opened_times = ndb.IntegerProperty(default=0)
    is_active = ndb.BooleanProperty(default=True)


    @classmethod
    def update_statistics(cls, 
                          tid,
                          used_times_delta=0,
                          replied_times_delta=0,
                          opened_times_delta=0):
        logging.info('tid %s' % tid)
        logging.info('used_times_delta %s' % used_times_delta)
        logging.info('replied_times_delta %s' % replied_times_delta)
        logging.info('opened_times_delta %s' % opened_times_delta)
        t = cls.find_by_properties(tid=tid)
        if t:
            t.used_times += used_times_delta
            t.replied_times += replied_times_delta
            t.opened_times += opened_times_delta
            t.put()
        else:
            logging.error('TemplarDoesNotExist %s' % tid)
        return t
        