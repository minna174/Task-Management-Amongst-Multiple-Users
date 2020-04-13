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

		taskboard_id = self.request.get('k')
		taskboard = ndb.Key(urlsafe=taskboard_id).get()
		template_values= {
			'taskboard' : taskboard
		}

		template= JINJA_ENVIRONMENT.get_template('viewtaskboard.html')
		self.response.write(template.render(template_values)) 
