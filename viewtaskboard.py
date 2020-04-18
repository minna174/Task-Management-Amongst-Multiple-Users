import webapp2
import os
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
from user import User
from taskboard import Taskboard
from task import Task #remove unused
from google.appengine.ext.db import Model
import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class ViewTaskBoard(webapp2.RequestHandler):
	def get(self):
		user=users.get_current_user()
		count_activetasks = 0
		count_completedtasks = 0
		count_completed_today = 0
		users_keys = []
		taskboard_key = self.request.get('k')
		taskboard = ndb.Key(urlsafe=taskboard_key).get()
		my_users = User.query().fetch(keys_only=True)
		logged_in_user = None

		for my_user in my_users:
			users_keys.append(my_user.get())
			if my_user.get().email_a == user.email():
				logged_in_user = my_user.get()

		if ndb.Key(urlsafe=taskboard_key) in logged_in_user.taskboards:
			tasks = []
			tasks_keys = []
			if taskboard.tasks:
				for task in taskboard.tasks:
					tasks.append(task.get())
					tasks_keys.append(task.urlsafe())
					if task.get().isCompleted == True:
						count_completedtasks = count_completedtasks + 1
						if task.get().completionDateTime.date() == datetime.datetime.today().date():
							count_completed_today = count_completed_today + 1
					else:
						count_activetasks = count_activetasks + 1

			template_values= {
				'taskboard' : taskboard,
				'taskboard_key' : taskboard_key,
				'my_users' : my_users,
				'users_keys' : users_keys,
				'user' : user,
				'tasks' : tasks,
				'tasks_keys' : tasks_keys,
				'count_activetasks' : count_activetasks,
				'count_completedtasks' : count_completedtasks,
				'count_completed_today' : count_completed_today
			}

			template= JINJA_ENVIRONMENT.get_template('viewtaskboard.html')
			self.response.write(template.render(template_values))
		else:
			self.redirect('/')

	def post(self):
		user=users.get_current_user()
		action = self.request.get('action')
		taskboard_key = self.request.get('taskboard_key')
		taskboard_key = ndb.Key(urlsafe=taskboard_key)
		taskboard = taskboard_key.get()

		if action == 'Invite':
			if user.email() == taskboard.owner.get().email_a:
				user_selected = self.request.get('user_keys_select')
				if user_selected == "chooseamemberuser":
					self.redirect("/ViewTaskBoard?k=" + taskboard_key.urlsafe())
				else:
					new_user_key = ndb.Key('User', user_selected)
					if new_user_key == taskboard.owner:
						template_values= {
							'message': 'You cannot invite the owner of a taskboard to itself. Choose a member user.'
						}
						template= JINJA_ENVIRONMENT.get_template('error.html')
						self.response.write(template.render(template_values))
					else:
						if new_user_key in taskboard.guests:
							template_values= {
								'message': 'Chosen user is already a member of this board.'
							}
							template= JINJA_ENVIRONMENT.get_template('error.html')
							self.response.write(template.render(template_values))
						else:
							new_user = new_user_key.get()
							new_user.taskboards.append(taskboard_key)
							new_user.put()
							taskboard.guests.append(new_user_key)
							taskboard.put()
							self.redirect("/ViewTaskBoard?k=" + taskboard_key.urlsafe())
			else:
				self.redirect('/')

		elif action == 'Add Task':
			#add task to this taskboard
			member_users = []
			member_users.append(taskboard.owner.get())

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
		elif action == 'Edit board':
			newtaskboardname = self.request.get('changename')
			taskboard.name = newtaskboardname
			taskboard.put()
			self.redirect("/ViewTaskBoard?k=" + taskboard_key.urlsafe())
		elif action == 'Edit task':
			task_key = self.request.get('task_key')
			task_key = ndb.Key(urlsafe=task_key)
			member_users = []
			member_users.append(taskboard.owner.get())

			for guest in taskboard.guests:
				member_users.append(guest.get())

			template_values= {
				'taskboard' : taskboard,
				'taskboard_key' : taskboard_key.urlsafe(),
				'user' : user,
				'task_key' : task_key.urlsafe(),
				'task' : task_key,
				'member_users' : member_users
			}
			template= JINJA_ENVIRONMENT.get_template('edittask.html')
			self.response.write(template.render(template_values))
		elif action == 'Delete task':
			#delete task from taskboard
			task_key = self.request.get('task_key')
			task_key = ndb.Key(urlsafe=task_key)
			for key in taskboard.tasks:
				if key == task_key:
					taskboard.tasks.remove(key)
					taskboard.put()
					key.delete()
			self.redirect('/ViewTaskBoard?k=' + taskboard_key.urlsafe())
		elif action == 'View and modify users':
			if user.email() == taskboard.owner.get().email_a:
				template_values= {
					'owner' : taskboard.owner,
					'guests' : taskboard.guests,
					'taskboard' : taskboard,
					'taskboard_key' : taskboard_key.urlsafe()
				}
				template= JINJA_ENVIRONMENT.get_template('viewmodifyusers.html')
				self.response.write(template.render(template_values))
		elif action == "Back":
			self.redirect('/')
		else:
			#clicked on checkbox to mark completion of task
			checkboxChecked = self.request.get('checkcompletion')
			task_key = self.request.get('task_key')
			task = ndb.Key(urlsafe=task_key).get()
			if checkboxChecked:
				task.isCompleted = True
				task.completionDateTime = datetime.datetime.utcnow()
				task.put()
			else:
				task.isCompleted = False
				task.completionDateTime = None
				task.put()
			self.redirect('/ViewTaskBoard?k=' + taskboard_key.urlsafe())
