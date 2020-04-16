from google.appengine.ext import ndb
from user import User

class Task(ndb.Model):
	title = ndb.StringProperty()
	duedate = ndb.DateProperty()
	isCompleted = ndb.BooleanProperty()
	assignee = ndb.KeyProperty(User)
	completionDateTime = ndb.DateTimeProperty()
