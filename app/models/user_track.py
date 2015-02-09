'''
Created on 2014/8/6

@author: sushih-wen
'''

from uuid import uuid4
from ferris import BasicModel
from google.appengine.ext import ndb


class UserTrack(BasicModel):
    ass = ndb.StringProperty()
    emails = ndb.StringProperty(repeated=True)  # user's email addresses of the same ass

    @staticmethod
    def new_ass():
        return str(uuid4())[-12:]
