from lib.py_bcrypt import bcrypt
from google.appengine.ext import db

class User(db.Model):
    ''' User is the user model for the app

        I'm using bcrypt to hash pws, which is more secure (and easier)
        than using hmac + generating salts
    '''
    username = db.StringProperty(required=True)
    password = db.TextProperty(required=True)
    email = db.StringProperty(required=True)
    create_date = db.DateTimeProperty(auto_now_add=True)

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
    def register(cls, username, password, email=None):
        hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())
        user = User(username=username, password=hashed_pw, email=email)
        return user


class Post(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    create_date = db.DateTimeProperty(auto_now_add=True)
    owner = db.ReferenceProperty(User)
    owner_id = db.StringProperty()
    modified_date = db.DateTimeProperty(auto_now=True)
    like_count = db.IntegerProperty(default=0)
    likes = db.StringListProperty()

    # shorthand method to get post id
    def get_id(self):
        return self.key().id()

    # replace plaintext line breaks with html line break
    def render(self):
        return self.content.replace('\n', '<br>')

    # renders first 500 chars of a post, for front page listing of posts
    def render_snippet(self):
        if len(self.content) > 500:
            return self.content[:500].replace('\n', '<br>') + '...'
        else:
            return self.content.replace('\n', '<br>')

    def get_likes(self):
        return self.likes

    # add a new like to a post
    def like(self, user_id):
        self.like_count += 1
        self.likes.append(str(user_id))
        print(str(user_id) + 'liked the thing')

    # determine if a user has already liked a post
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
    comment = db.TextProperty(required=True)
    user = db.ReferenceProperty(
        User, collection_name='comments', required=True)
    post = db.ReferenceProperty(
        Post, collection_name='comments', required=True)
    username = db.StringProperty(required=True)
    create_date = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_comments(cls, post=None):
        if post:
            return cls.all().filter('post = ', post).run()
        else:
            return cls.all().run()

    def render(self):
        return self.comment.replace('\n', '<br>')
