'''
Created on 2014/8/19

@author: sushih-wen
'''
from ferris import BasicModel
from google.appengine.ext import ndb


class Link(BasicModel):

    """
    Parse the url to be combination of token(id of an email) and url_id

    http://www.google.com
    => https://zenblip.appspot.com/l?t=2q4tk3gqg5&h=q4tqlkgqlkq5gq5
    """

    token = ndb.StringProperty(required=True)
    sender = ndb.StringProperty(required=True)
    url_id = ndb.StringProperty(required=True)  # hash of url
    url = ndb.TextProperty(required=True)  # TextProperty: due to 500 characters limit
    access_count = ndb.IntegerProperty(default=0)
    subject = ndb.TextProperty() #email subject
    receiver_emails = ndb.StringProperty(repeated=True)
    country = ndb.TextProperty() #last access
    city = ndb.TextProperty() #last access
    device = ndb.TextProperty() #last access
    is_accessed = ndb.BooleanProperty()
