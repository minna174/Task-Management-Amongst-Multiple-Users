import webapp2
import os
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.db import Model
from user import User
from taskboard import Taskboard
from task import Task
from viewtaskboard import ViewTaskBoard
import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class EditTask(webapp2.RequestHandler):
	def post(self):
		action = self.request.get('submitaction')
		task_key = self.request.get('task_key')
		taskboard_key = self.request.get('taskboard_key')
		taskboard_key = ndb.Key(urlsafe=taskboard_key)
		taskboard = taskboard_key.get()

		if action == 'Edit':
			title = self.request.get('title')
			duedate = self.request.get('duedate')
			isCompleted = self.request.get('completed')
			assignee_emailaddress = self.request.get('assigned_member')
			if assignee_emailaddress == 'I will assign later':
				assignee_emailaddress = ''
				assignee = None
			else:
				assignee = ndb.Key(User, assignee_emailaddress)
			if isCompleted:
				isCompleted = True
			else:
				isCompleted = False

			#check if name is unique
			if taskboard.tasks:
				for task in taskboard.tasks:
					task = task.get()
					if task.title == title:
						#this title already exists for some task in this taskboard
						template_values= {
			                'message': 'A task with same title exists already. Choose differnt name.'
			            }
						template= JINJA_ENVIRONMENT.get_template('error.html')
						self.response.write(template.render(template_values))

			#add to datastore
			task = ndb.Key(urlsafe=task_key).get()
			if task:
				task.title = title
				task.duedate = datetime.datetime(int(duedate.split("-")[0]), int(duedate.split("-")[1]), int(duedate.split("-")[2]))
				task.isCompleted = isCompleted
				task.assignee = assignee
				task.put()
				self.redirect('/ViewTaskBoard?k=' + taskboard_key.urlsafe())
			else:
				template_values= {
	                'message': 'Some problem occurred, please try again'
	            }
				template= JINJA_ENVIRONMENT.get_template('error.html')
				self.response.write(template.render(template_values))
		elif action == "Back":
			self.redirect('/ViewTaskBoard?k=' + taskboard_key.urlsafe())
