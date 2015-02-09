'''
Created on 2014/8/24

@author: sushih-wen
'''
from ferris import BasicModel
from google.appengine.ext import ndb
from google.appengine.api import users


class ChannelClient(BasicModel):
    owner = ndb.StringProperty(required=True)
    client_id = ndb.StringProperty(required=True)
    channel_token = ndb.TextProperty()

    def to_dict_output(self, include=['client_id', 'channel_token'], exclude=[]):
        return self.to_dict(include=include, exclude=exclude)
