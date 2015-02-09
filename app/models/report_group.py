'''
Created on 2014/10/4

@author: sushih-wen
'''

from ferris import BasicModel
from google.appengine.ext import ndb


class ReportGroup(BasicModel):

    """
    Used to build report group.
    the orgs are mapped to the orgs in UserInfo

    We setup the report in cron.yaml
    The report can be sent freely.
    1. for a person himself from any time of a certain period
    2. for a manage team to read report of an org of people

    This report group is set for purpose 2


    """
    rgid = ndb.StringProperty()  # used to specified the report group
    orgs = ndb.StringProperty(repeated=True)
    to = ndb.StringProperty(repeated=True)  # email receivers
