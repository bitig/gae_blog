#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
import hmac
import random
from lib.py_bcrypt import bcrypt
from google.appengine.ext import db

# root dir of blog
HOME_PATH = '/blog'

# initialize jinga2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
                            loader = jinja2.FileSystemLoader(template_dir),
                            autoescape = True
                            )

# secret for secure cookie has - should not be here in a production server
secret = 'rastfydguhiujimiqwo'

# secure cookies
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

# parent handler extends webapp2.RequestHandler with convenience methods
class Handler(webapp2.RequestHandler):
    # shorthand write
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    # generate HTML from template
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, user = None, **kw):
        if not user:
            user = self.user
        self.write(self.render_str(template, user = user, **kw))

    # generic methods to set/read any cookies
    def set_secure_cookie(self, name, val):
        sec_val = make_secure_val(val)
        self.response.set_cookie(name, sec_val)

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    # method to set secure login cookie
    def set_login_cookie(self, user):
        self.set_secure_cookie('user_id', str(user.get_id()))

    # logs user out
    def remove_login_cookie(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    # redirects to login
    def redirect_to_login(self):
        self.redirect(HOME_PATH + '/login/')

    # return the unsecured user_id if the user is logged in, otherwise return None
    def logged_in(self):
        secure_uid = self.read_secure_cookie('user_id')
        if secure_uid:
            uid = secure_uid.split('|')[0]
            if uid.isdigit():
                return uid

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        # set user on every request
        uid = self.logged_in()
        self.user = uid and User.by_id(int(uid))


class User(db.Model):
    username = db.StringProperty(required = True)
    password = db.TextProperty(required = True)
    email = db.StringProperty(required = True)
    create_date = db.DateTimeProperty(auto_now_add = True)

    # @classmethod
    def verify_pw(self, password):
        if bcrypt.hashpw(password, self.password) == self.password:
            return True

    def get_id(self):
        return self.key().id()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid)

    @classmethod
    def by_name(cls, name):
        return User.all().filter('username = ', name).get()

    @classmethod
    def register(cls, username, password, email = None):
        hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())
        user = User(username = username, password = hashed_pw, email = email)
        return user

class Post(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    create_date = db.DateTimeProperty(auto_now_add = True)
    owner = db.ReferenceProperty(User)
    owner_id = db.StringProperty()
    modified_date = db.DateTimeProperty(auto_now = True)
    like_count = db.IntegerProperty(default = 0)
    likes = db.StringListProperty()

    def get_id(self):
        return self.key().id()

    def render(self):
        return self.content.replace('\n', '<br>')

    def render_snippet(self):
        if len(self.content) > 150:
            return self.content[:150].replace('\n', '<br>') + '...'
        else:
            return self.content.replace('\n', '<br>')

    def get_likes(self):
        return self.likes

    def like(self, user_id):
        self.like_count += 1
        self.likes.append(str(user_id))
        print(str(user_id) + 'liked the thing')

    def already_liked(self, user_id):
        print self.likes
        if self.likes.count(str(user_id)) > 0:
            return True

    def is_creator(self, user_id):
        if int(self.owner_id) == int(user_id):
            return True

    @classmethod
    def by_id(cls, pid):
        return cls.get_by_id(pid)


class Comment(db.Model):
    comment = db.TextProperty(required = True)
    user = db.ReferenceProperty(User, collection_name = 'comments', required = True)
    post = db.ReferenceProperty(Post, collection_name = 'comments', required = True)
    username = db.StringProperty(required = True)
    create_date = db.DateTimeProperty(auto_now_add = True)

    @classmethod
    def get_comments(cls, post = None):
        if post:
            return cls.all().filter('post = ', post).run()
        else:
            return cls.all().run()

class MainPage(Handler):

    def render_front(self, title = "", blog = "", error = ""):
        posts = db.GqlQuery('SELECT * FROM Post')
        print(posts)
        if not posts:
            error = 'Sorry, there are no posts on the blog yet.'
        self.render("blog.html", error = error, posts = posts)

    def get(self):
        self.render_front()

class SubmitHandler(Handler):

    def get_post(self, id_str):
        post_id = None
        if id_str and id_str.isdigit():
            post_id = int(id_str)
        post = None
        if post_id:
            post = Post.get_by_id(post_id)
        return post

    def render_form(self, title = '', content = '', title_error = '', content_error = ''):
        self.render("form.html", title = title, content = content, title_error = title_error, content_error = content_error)

    def post(self, post_id = None):
        if self.user:

            title = self.request.get('subject')
            content = self.request.get('content')

            if title and content:
                # if editing, there will be a post_id defined
                if post_id:
                    post = self.get_post(post_id)
                    print self.user.get_id() == int(post.owner_id)
                    if post and self.user.get_id() == int(post.owner_id):
                        post.title = title
                        post.content = content
                        post.put()
                        self.redirect(HOME_PATH + '/' + str(post.key().id()) + '/')
                    else:
                        self.redirect_to_login()
                else:
                    # create a new post
                    post = Post(title = title, content = content, owner_id = str(self.user.get_id()), owner = self.user)
                    post.put()
                    self.redirect(HOME_PATH + '/' + str(post.key().id()) + '/')
            else:
                title_error = ''
                content_error = ''
                if not title:
                    title_error = 'Title is required!'
                if not content:
                    content_error = 'Content is required!'
                self.render_form(title, content, title_error = title_error, content_error = content_error)
        else:
            self.redirect_to_login()

class NewPost(SubmitHandler):

    def get(self):
        if self.user:
            self.render_form()
        else:
            self.redirect_to_login()

class EditPost(SubmitHandler):

    def get(self, id_str):

        post = self.get_post(id_str)
        # you can edit if you are logged in, give a valid post, and are owner
        if post and self.user and int(post.owner_id) == self.user.get_id():
            self.render("form.html", title = post.title, content = post.content)
        else:
            self.redirect(HOME_PATH + '/login/')


class BlogPage(Handler):

    def get(self, digits):
        requested_id = int(digits)
        key = db.Key.from_path('Model', requested_id)
        post = db.get(key)
        post = Post.get_by_id(requested_id)
        error = ''
        comments = Comment.get_comments(post)
        if not post:
            error = 'Requested post not found :('
        if comments:
            self.render("post.html", error = error, post = post, comments = comments)
        else:
            self.render("post.html", error = error, post = post)


class SignupPage(Handler):
    def render_form(self, username = '', email = '', errors = ''):
        self.render("signup.html", username = username, email = email, errors = errors)

    def get(self):
        self.render_form()

    def post(self):
        # get all the required params
        username = self.request.get('username')
        password = self.request.get('password')
        email = self.request.get('email')
        verify = self.request.get('verify')

        # build an array of errors
        # if there is any error set return_error to true
        errors = []
        return_error = False
        if not username or not password or not email or not verify:
            return_error = True
            errors.append('All fields are required.')
        if password != verify:
            return_error = True
            errors.append('Passwords did not match.')
        if username:
            # check if username exists
            u = User.by_name(username)
            if u:
                errors.append('That username is already taken.')
                return_error = True

        if return_error == True:
            self.render_form(username, email, errors)
        else:
            user = User.register(username, password, email)
            user.put()
            self.set_login_cookie(user)
            self.redirect(HOME_PATH + '/welcome')

class WelcomePage(Handler):
    def get(self):
        if self.user:
            self.render("welcome.html", username = self.user.username)
        else:
            self.redirect(HOME_PATH + '/signup')

class LoginPage(Handler):
    def render_form(self, username = '', errors = ''):
        self.render("login.html", username = username, errors = errors)

    def get(self):
        self.render_form()

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        errors = []
        user = User.by_name(username)
        if user:
            if user.verify_pw(password):
                self.set_login_cookie(user)
                self.render('welcome.html', user = user)
            else:
                errors.append('Invalid password.')
                self.render_form(username = username, errors = errors)
        else:
            errors.append('No user with that username was found.')
            self.render_form(username = username, errors = errors)

class Logout(Handler):

    def post(self):
        self.remove_login_cookie()
        self.redirect(HOME_PATH + '/signup/')


class LikeHandler(Handler):

    def post(self, digits):
        post_id = digits
        post = None
        if digits.isdigit():
            post = Post.get_by_id(int(post_id))

        message = ''

        # if user_id is not None, the user is logged in
        if self.user:
            if post:
                uid = str(self.user.get_id())
                if post.already_liked(uid):
                    message = 'You already liked this.'
                if post.is_creator(uid):
                    message = 'You can\'t like your own post.'
                if not post.already_liked(uid) and not post.is_creator(uid):
                    post.like(uid)
                    post.put()
            else:
                self.response.set_status(422)
                message = 'The requested post or user was not found.'
        else:
            message = 'You must <a href="/blog/login/">sign in</a> or <a href="/blog/signup/">create an account</a> to comment.'

        self.render('snippet/likes.html', post = post, message = message)


class CommentHandler(Handler):
    def post(self, digits):
        post_id = digits
        message = self.request.body

        if self.user and post_id.isdigit():
            post = Post.get_by_id(int(post_id))
            if post and self.user and message:
                comment = Comment(username = self.user.username, user = self.user, post = post, comment = message)
                comment.put()
                self.render("snippet/comment.html", comment = comment, post = post)
            else:
                self.response.set_status(422)
                self.response.write('There was a problem with the requested post, user, or comment.')
        else:
            self.response.set_status(403)
            self.response.write('You must log in to comment.')

class DeleteHandler(Handler):
    def post(self, post_id):

        if post_id and post_id.isdigit():
            post = Post.get_by_id(int(post_id))


        if self.user and post and post.owner_id == str(self.user.get_id()):
            title = post.title
            db.delete(post.key())
            self.render("deleted.html", title = title) # TODO: better user feedback
        else:
            self.redirect_to_login()





app = webapp2.WSGIApplication([
    (HOME_PATH + '/', MainPage),
    (HOME_PATH + '/newpost/', NewPost),
    (HOME_PATH + '/edit/(\d+)/', EditPost),
    (HOME_PATH + '/(\d+)/', BlogPage),
    (HOME_PATH + '/login/', LoginPage),
    (HOME_PATH + '/logout/', Logout),
    (HOME_PATH + '/signup/', SignupPage),
    (HOME_PATH + '/welcome/', WelcomePage),
    (HOME_PATH + '/like/(\d+)/', LikeHandler),
    (HOME_PATH + '/comment/(\d+)/', CommentHandler),
    (HOME_PATH + '/delete/(\d+)/', DeleteHandler)
    ], debug = True)
