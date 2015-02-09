from ferris import BasicModel
from google.appengine.ext import ndb
from google.appengine.api import users


class Access(BasicModel):

    """


    """
    token = ndb.StringProperty(required=True)  # stored for thread query
    sender = ndb.StringProperty(required=True)  # owner of this access knowledge
    url = ndb.StringProperty()
    kind = ndb.StringProperty(choices=['open', 'link'])
    accessor = ndb.StringProperty()  # accessor email, if identified
    accessor_name = ndb.StringProperty()  # accessor name, if identified
    ass = ndb.StringProperty()  # accessor cookie id
    ip = ndb.StringProperty()
    country = ndb.StringProperty()
    city = ndb.StringProperty()
    user_agent = ndb.StringProperty()
    proxy = ndb.StringProperty()
    device = ndb.StringProperty()
    tz_offset = ndb.IntegerProperty()

    def to_dict_output(self, include=['token', 'sender', 'url', 'kind',
                                      'accessor', 'accessor_name', 'country', 'city'], exclude=[]):
        return self.to_dict(include=include, exclude=exclude)
