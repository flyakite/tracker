from ferris import BasicModel
from google.appengine.ext import ndb
from google.appengine.api import users


class Relation(BasicModel):

    """
    rel(relations): knows

    """
    a = ndb.StringProperty(required=True)  # email
    rel = ndb.StringProperty(required=True, choices=['knows', ])
    b = ndb.StringProperty(required=True)  # email
