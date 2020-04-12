import webapp2
import os
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.db import Model
from user import User
from taskboard import Taskboard
from task import Task

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class Mainpage(webapp2.RequestHandler):
    def get(self):
        # self.response.write('sjdfh')
        self.response.headers['Content-type']='text/html'
        url=''
        url_string=''
        user=users.get_current_user()
        currentUser=None
        if user:
            url=users.create_logout_url(self.request.uri)
            url_string='logout'
            currentUser_key=ndb.Key('User',user.email())
            currentUser=currentUser_key.get()
            if currentUser == None:
                currentUser= User(id=user.email(), email_a=user.email())
                currentUser.put()
        else:
            url= users.create_login_url(self.request.uri)
            url_string= 'login'

        template_values= {
            'url': url,
            'url_string': url_string,
            'user': user
        }

        template= JINJA_ENVIRONMENT.get_template('mainpage.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', Mainpage), ('/user', User), ('/task', Task), ],debug=True)
