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
		task = ndb.Key(urlsafe=task_key).get()
		canProceed = False

		if action == 'Edit':
			title = self.request.get('title').strip()
			duedate = self.request.get('duedate')
			isCompleted = self.request.get('completed')
			assignee_emailaddress = self.request.get('assigned_member')
			if assignee_emailaddress == 'assignLater':
				assignee_emailaddress = ''
				assignee = None
			else:
				assignee = ndb.Key(User, assignee_emailaddress)
			if isCompleted:
				isCompleted = True
			else:
				isCompleted = False

			if ((task.duedate != duedate) and (datetime.datetime.strptime(duedate, "%Y-%m-%d").date() < datetime.datetime.today().date())):
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
						for t in taskboard.tasks:
							t = t.get()
							if t.title == title:
								#this title already exists for some task in this taskboard
								template_values= {
					                'message': 'A task with same title exists already. Choose differnt name.'
					            }
								template= JINJA_ENVIRONMENT.get_template('error.html')
								self.response.write(template.render(template_values))

					#add to datastore
					if task:
						task.title = title
						task.duedate = datetime.datetime(int(duedate.split("-")[0]), int(duedate.split("-")[1]), int(duedate.split("-")[2]))
						task.isCompleted = isCompleted
						task.assignee = assignee
						if isCompleted == True:
							task.completionDateTime = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
						else:
							task.completionDateTime = None
						task.put()
						self.redirect('/ViewTaskBoard?k=' + taskboard_key.urlsafe())
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
		elif action == "Back":
			self.redirect('/ViewTaskBoard?k=' + taskboard_key.urlsafe())
