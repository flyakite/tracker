'''
Created on 2014/9/22

@author: sushih-wen
'''

import logging
from ferris import BasicModel
from google.appengine.ext import ndb
from google.appengine.ext import deferred
from ferris.core import mail
#from app.utils import is_email_valid


class UserInfo(BasicModel):
    email = ndb.StringProperty()
    name = ndb.StringProperty()
    given_name = ndb.StringProperty()
    family_name = ndb.StringProperty()
    picture = ndb.TextProperty()
    gender = ndb.StringProperty()
    locale = ndb.StringProperty()
    orgs = ndb.StringProperty(repeated=True)
    last_seen = ndb.DateTimeProperty()

    domain = ndb.StringProperty()  # email domain part, in lower case
    role = ndb.IntegerProperty()  # null or 0: not legit, 1:free plan, 2:pro plan 3:team plan
    started = ndb.DateTimeProperty()  # the datetime the user send first signal, used for scheduled news letter
    tz_offset = ndb.IntegerProperty(default=0)

    google_id = ndb.StringProperty()
    refresh_token = ndb.StringProperty()

    @classmethod
    def create_user(cls,
                    email,
                    name=None,
                    given_name=None,
                    family_name=None,
                    picture=None,
                    gender=None,
                    locale=None,
                    orgs=[],
                    last_seen=None,
                    domain=None,
                    role=None,
                    started=None,
                    tz_offset=None,
                    google_id=None,
                    created=None,
                    save=True,
                    sync=True):

        # TODO: check parameters

        u = cls(
            email=email,
            name=name,
            given_name=given_name,
            family_name=family_name,
            picture=picture,
            gender=gender,
            locale=locale,
            orgs=orgs,
            last_seen=last_seen,
            domain=domain,
            role=role,
            started=started,
            tz_offset=tz_offset,
            google_id=google_id,
            created=created
            )

        if save:
            u.put() if sync else u.put_async()

        return u

    @staticmethod
    def send_email(receiver, title, template_name, sync=False):

        logging.info('send_email %s %s %s' % (receiver, title, template_name))
        args = [receiver, title]
        # sender settings in settings.py
        kwargs = dict(template_name=template_name,
                      context={})

        if sync:
            mail.send_template(*args, **kwargs)
        else:
            # Pickling of datastore_query.PropertyOrder is unsupported.
            deferred.defer(mail.send_template, *args, **kwargs)

    def is_self_legit(self):
        if self.role and self.role >= 1:
            return True
        else:
            return False
