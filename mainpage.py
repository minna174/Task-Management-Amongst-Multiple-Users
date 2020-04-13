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

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class Mainpage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-type']='text/html'
        url=''
        url_string=''
        user=users.get_current_user()
        currentUser=None
        my_boards = []
        temp = []
        keys=[]
        currentUser_key=[]
        if user:
            url=users.create_logout_url(self.request.uri)
            url_string='logout'
            currentUser_key=ndb.Key('User',user.email())
            currentUser=currentUser_key.get()
            if currentUser == None:
                currentUser= User(id=user.email(), email_a=user.email())
                currentUser.put()
            else:
                my_boards = currentUser.taskboards
        else:
            url= users.create_login_url(self.request.uri)
            url_string= 'login'

        if my_boards:
            for board in my_boards:
                temp.append(board.get())
                keys.append(board.urlsafe())
            my_boards = temp

        template_values= {
            'url': url,
            'url_string': url_string,
            'user': user,
            'my_boards' : my_boards,
            'user_key' : currentUser_key,
            'keys' : keys
        }

        template= JINJA_ENVIRONMENT.get_template('mainpage.html')
        self.response.write(template.render(template_values))

    def post(self):
        user=users.get_current_user()
        if user:
            url=users.create_logout_url(self.request.uri)
            url_string='logout'
            currentUser_key=ndb.Key('User',user.email())
            currentUser=currentUser_key.get()

            boardname = self.request.get('boardname').strip()
            button = self.request.get('button')
            if button == 'New board':
                #creating new board
                taskboard = Taskboard()
                taskboard.name = boardname
                taskboard.owner = currentUser_key
                key = taskboard.put()
                currentUser.taskboards.append(key)
                currentUser.put()
                self.redirect('/')
        else:
            template_values= {
                'message' : 'Please login to create new taskboard'
            }

            template= JINJA_ENVIRONMENT.get_template('error.html')
            self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', Mainpage), ('/user', User), ('/task', Task), ('/taskboard', Taskboard), ('/viewtaskboard', ViewTaskBoard), ],debug=True)
