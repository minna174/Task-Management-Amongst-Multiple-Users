from google.appengine.ext import ndb

class Task(ndb.Model):
	name = ndb.StringProperty()
	duedate = ndb.DateProperty()
