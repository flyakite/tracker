'''
Created on 2014/11/28

@author: sushih-wen
'''
from ferris import BasicModel
from google.appengine.ext import ndb


class Domain(BasicModel):
    domain = ndb.StringProperty()
    position = ndb.IntegerProperty()

    def is_legit(self):
        if self.position == 1:
            return True
        else:
            return False
