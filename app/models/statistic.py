'''
Created on 2015/2/19

@author: sushih-wen
'''
import logging
from ferris import BasicModel
from google.appengine.ext import ndb
from google.appengine.ext import deferred
from ferris.core import mail
#from app.utils import is_email_valid


class Statistic(BasicModel):
    email = ndb.StringProperty()
    monthly_signal_count = ndb.IntegerProperty(default=0)

    @classmethod
    def create(cls,
               email,
               monthly_signal_count=1,
               ):

        statistic = cls(email=email,
                        monthly_signal_count=monthly_signal_count
                        )
        statistic.put()
        return statistic
