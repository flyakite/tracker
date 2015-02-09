'''
Created on 2014/12/15

@author: sushih-wen
'''

from ferris import BasicModel
from google.appengine.ext import ndb


class DeviceClient(BasicModel):
    owner = ndb.StringProperty(required=True)
    client_id = ndb.StringProperty(required=True)
    client_name = ndb.StringProperty()

    def to_dict_output(self, include=['client_id'], exclude=[]):
        return self.to_dict(include=include, exclude=exclude)
