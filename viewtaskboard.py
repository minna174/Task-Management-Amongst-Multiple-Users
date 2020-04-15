import webapp2
import os
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
from user import User
from taskboard import Taskboard
from task import Task #remove unused
from google.appengine.ext.db import Model

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class ViewTaskBoard(webapp2.RequestHandler):
	def get(self):
		user=users.get_current_user()
		users_keys = []
		taskboard_key = self.request.get('k')
		taskboard = ndb.Key(urlsafe=taskboard_key).get()
		my_users = User.query().fetch(keys_only=True)
		for my_user in my_users:
			users_keys.append(my_user.get())

		tasks = []
		tasks_keys = []
		if taskboard.tasks:
			for task in taskboard.tasks:
				tasks.append(task.get())
				tasks_keys.append(task.urlsafe())

		template_values= {
			'taskboard' : taskboard,
			'taskboard_key' : taskboard_key,
			'my_users' : my_users,
			'users_keys' : users_keys,
			'user' : user,
			'tasks' : tasks,
			'tasks_keys' : tasks_keys
		}

		template= JINJA_ENVIRONMENT.get_template('viewtaskboard.html')
		self.response.write(template.render(template_values))

	def post(self):
		user=users.get_current_user()
		action = self.request.get('action')
		taskboard_key = self.request.get('taskboard_key')
		taskboard_key = ndb.Key(urlsafe=taskboard_key)
		taskboard = taskboard_key.get()

		if action == 'Invite':
			if user.email() == taskboard.owner.get().email_a:
				user_selected = self.request.get('user_keys_select')
				new_user_key = ndb.Key('User', user_selected)
				new_user = new_user_key.get()
				new_user.taskboards.append(taskboard_key)
				new_user.put()
				taskboard.guests.append(new_user_key)
				taskboard.put()
				self.redirect('/')
			else:
				self.redirect('/')

		elif action == 'Add Task':
			#add task to this taskboard
			member_users = []
			for guest in taskboard.guests:
				member_users.append(guest.get())

			template_values= {
				'taskboard' : taskboard,
				'taskboard_key' : taskboard_key.urlsafe(),
				'user' : user,
				'member_users' : member_users
			}
			template= JINJA_ENVIRONMENT.get_template('addtask.html')
			self.response.write(template.render(template_values))
