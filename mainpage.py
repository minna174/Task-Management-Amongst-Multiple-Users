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
from addtask import AddTask
from edittask import EditTask

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
        total_boards = []
        own_boards = []
        own_board_keys = []
        member_board_keys = []
        member_boards = []
        currentUser_key = None
        if user:
            url=users.create_logout_url(self.request.uri)
            url_string='logout'
            currentUser_key=ndb.Key('User', user.email())
            currentUser=currentUser_key.get()
            if currentUser == None:
                currentUser= User(id=user.email(), email_a=user.email())
                currentUser.put()
            else:
                total_boards = currentUser.taskboards
        else:
            url= users.create_login_url(self.request.uri)
            url_string= 'login'

        if total_boards:
            for board in total_boards:
                if board.get().owner.get().email_a == user.email():
                    own_boards.append(board)
                    own_board_keys.append(board.urlsafe())
                else:
                    member_boards.append(board)
                    member_board_keys.append(board.urlsafe())


        template_values= {
            'url': url,
            'url_string': url_string,
            'user': user,
            'total_boards' : total_boards,
            'own_boards' : own_boards,
            'member_boards' : member_boards,
            'user_key' : currentUser_key,
            'own_board_keys' : own_board_keys,
            'member_board_keys' : member_board_keys
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
                if len(boardname) > 0:
                    taskboard = Taskboard()
                    taskboard.name = boardname
                    taskboard.owner = currentUser_key
                    key = taskboard.put()
                    currentUser.taskboards.append(key)
                    currentUser.put()
                    self.redirect('/')
                else:
                    template_values= {
                        'message': 'Taskboard name cannot be empty'
                    }

                    template= JINJA_ENVIRONMENT.get_template('error.html')
                    self.response.write(template.render(template_values))
        else:
            template_values= {
                'message': 'Please login to create a new taskboard'
            }

            template= JINJA_ENVIRONMENT.get_template('error.html')
            self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', Mainpage), ('/User', User), ('/Task', Task), ('/Taskboard', Taskboard), ('/ViewTaskBoard', ViewTaskBoard), ('/AddTask', AddTask), ('/EditTask', EditTask),],debug=True)
