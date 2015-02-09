'''
Created on 2015/1/21

@author: sushih-wen
'''
import json
import logging
from datetime import datetime, timedelta
from uuid import uuid4
from google.appengine.ext import testbed
from ferrisnose import AppEngineTest, AppEngineWebTest, FerrisAppTest
from app.models.user_info import UserInfo


class TestBase(AppEngineWebTest):

    """
    test
    """

    def setUp(self):
        AppEngineWebTest.setUp(self)

    def createUser(self, 
                   sender='sender@asdf.com',
                   name='KJ Chang',
                   given_name='KJ',
                   family_name='Change',
                   picture='https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg',
                   gender='male',
                   locale='en',
                   orgs=['test'], 
                   role=0, 
                   tz_offset=9,
                   last_seen=datetime.utcnow() - timedelta(days=1),
                   domain='asdf.com',
                   google_id='1234567890123456789',
                   ):
        
                    
        user = UserInfo.create_user(
            email=sender,
            name=name,
            given_name=given_name,
            family_name=family_name,
            picture=picture,
            gender=gender,
            locale=locale,
            orgs=orgs,
            role=role,
            tz_offset=tz_offset,
            last_seen=last_seen,
            domain=domain,
            google_id=google_id
        )
        user.put()
        return user
        
    def createLegitUser(self):
        return self.createUser(role=1)
        
class TestBaseWithMail(TestBase):
    
    def setUp(self):
        TestBase.setUp(self)
        self.mail_stub = self.testbed.testbed.get_stub(testbed.MAIL_SERVICE_NAME)