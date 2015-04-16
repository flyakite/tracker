'''
Created on 2015/4/12

@author: sushih-wen
'''
from test_base import TestBase
from ferris import settings
from app.libs.google_client import GoogleClient


class TestGoogleClient(TestBase):

    def setUp(self):
        super(TestBase, self).setUp()

    def test_obtain_new_access_token_from_refresh_token(self):
        """
        TODO: create test account
        """
        pass

    def test_get_resource(self):
        pass
