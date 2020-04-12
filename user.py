from google.appengine.ext import ndb

class User(ndb.Model):
    email_a = ndb.StringProperty()
    taskboards = ndb.KeyProperty(kind='Taskboard', repeated=True)
