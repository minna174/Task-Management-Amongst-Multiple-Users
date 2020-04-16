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
			completionDateTime = datetime.datetime.now()
		else:
			isCompleted = False
			completionDateTime = None

		#check if name is unique
		if taskboard.tasks:
		    for task in taskboard.tasks:
		        task = task.get()
		        if task:
		            if task.title == title:
		                task_exists = True

		if task_exists == True:
		    #this title already exists for some task in this taskboard
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
