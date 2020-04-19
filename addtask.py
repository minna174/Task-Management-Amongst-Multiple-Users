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

class AddTask(webapp2.RequestHandler):

	def post(self):
		taskboard_key = self.request.get('taskboard_key')
		taskboard_key = ndb.Key(urlsafe=taskboard_key)
		taskboard = taskboard_key.get()
		task_exists = False
		title = self.request.get('title').strip()
		duedate = self.request.get('duedate')
		assignee_emailaddress = self.request.get('assigned_member')
		isCompleted = False
		completionDateTime = None

		if assignee_emailaddress == 'assignLater':
			assignee_emailaddress = ''
			assignee = None
		else:
			assignee = ndb.Key(User, assignee_emailaddress)

		#check if duedate is before today
		if datetime.datetime.strptime(duedate, "%Y-%m-%d").date() < datetime.datetime.today().date():
			template_values= {
				'message': 'Please select a date greater than or equal to today',
				'path' : '/ViewTaskBoard?k=' + taskboard_key.urlsafe()
			}
			template= JINJA_ENVIRONMENT.get_template('error.html')
			self.response.write(template.render(template_values))
		else:
			if len(title) > 0:
				#check if name is unique
				if taskboard.tasks:
					for task in taskboard.tasks:
					    task = task.get()
					    if task:
					        if task.title == title:
					            task_exists = True

				if task_exists == True:
					template_values= {
						'message': 'A task with same title exists already. Choose differnt name.'
					}
					template= JINJA_ENVIRONMENT.get_template('error.html')
					self.response.write(template.render(template_values))
				else:
					task = Task(
						title = title,
						duedate = datetime.datetime(int(duedate.split("-")[0]), int(duedate.split("-")[1]), int(duedate.split("-")[2])),
						isCompleted = isCompleted,
						assignee = assignee,
						completionDateTime = completionDateTime)
					if task:
						task_key = task.put()
						taskboard.tasks.append(task_key)
						taskboard.put()
						self.redirect("/ViewTaskBoard?k=" + taskboard_key.urlsafe())
					else:
						template_values= {
					        'message': 'Some problem occurred, please try again'
					    }
						template= JINJA_ENVIRONMENT.get_template('error.html')
						self.response.write(template.render(template_values))
			else:
				template_values= {
					'message': 'Title cannot be empty',
					'path' : '/ViewTaskBoard?k=' + taskboard_key.urlsafe()
				}
				template= JINJA_ENVIRONMENT.get_template('error.html')
				self.response.write(template.render(template_values))
