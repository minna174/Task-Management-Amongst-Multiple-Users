import webapp2
import os
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
from user import User
from taskboard import Taskboard
from task import Task
from google.appengine.ext.db import Model
import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class ViewModifyUsers(webapp2.RequestHandler):
	def get(self):
		taskboard_key = self.request.get('taskboard_key')
		taskboard_key = ndb.Key(urlsafe=taskboard_key)
		taskboard = taskboard_key.get()

		deluser_key = self.request.get('deluser')
		deluser_key = ndb.Key(urlsafe=deluser_key)
		deluser = deluser_key.get()

		#remove the user from guests, guests_assigned properties of taskboard
		#remove the taskboard from taskboards property of User modal
		guests_ = taskboard.guests
		guests_assigned_ = taskboard.guests_assigned
		tasks_ = taskboard.tasks

		res = ''
		for guest in guests_:
			if guest.get().email_a == deluser.email_a:
				user_taskboards = guest.get().taskboards
				for tboard in user_taskboards:
					if tboard == taskboard_key:
						# taskboard.delete()
						guest.get().taskboards.remove(tboard)
						guest.get().put()
						res = res + 'one'
				guests_.remove(guest)
				res = res + ':four'

		#if any of the task in tasks property of the taskboard have assignee prooperty as 'deluser', modify the task: set it as unassigned and highlight red
		if tasks_:
			for task in tasks_:
				if task.get():
					if task.get().assignee and (task.get().assignee == deluser_key):
						task.get().assignee = None
						task.get().put()
						res = res + ':five'

		else:
			res = res + ':six'

		taskboard.put()
		self.redirect('/ViewTaskBoard?k=' + taskboard_key.urlsafe())
