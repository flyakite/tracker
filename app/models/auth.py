'''
Created on 2014/12/27

@author: sushih-wen
'''

import logging
import httplib2
import logging
import os
import pickle
from datetime import datetime
from ferris import BasicModel
from google.appengine.ext import ndb
from ferris import settings
from libs.googleapiclient.apiclient import discovery
from libs.googleapiclient.oauth2client import appengine, client
from google.appengine.api import memcache

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'config/google_client_secrets.json')
http = httplib2.Http(memcache)
service = discovery.build("plus", "v1", http=http)
decorator = appengine.oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/plus.me')


class ApiKey(BasicModel):
    pass
