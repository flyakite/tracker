
'''
Created on 2014/8/21

@author: sushih-wen
'''

from ferris import route_with
from base import BaseController


class Main(BaseController):

    @route_with('/')
    def index(self):
        pass
