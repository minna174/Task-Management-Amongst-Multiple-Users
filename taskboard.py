from google.appengine.ext import ndb
from user import User
from task import Task

class Taskboard(ndb.Model):
	name = ndb.StringProperty()
	owner = ndb.KeyProperty(User)
	tasks = ndb.KeyProperty(Task, repeated=True)
	guests = ndb.KeyProperty(User, repeated=True)
	guests_assigned = ndb.KeyProperty(User, repeated=True)
