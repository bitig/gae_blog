
from lib.py_bcrypt import bcrypt
from google.appengine.ext import ndb


class User(ndb.Model):
    ''' User is the user model for the app

        I'm using bcrypt to hash pws, which is more secure (and easier)
        than using hmac + generating salts
    '''
    username = ndb.StringProperty(required=True)
    password = ndb.TextProperty(required=True)
    email = ndb.StringProperty(required=True)
    create_date = ndb.DateTimeProperty(auto_now_add=True)

    def verify_pw(self, password):
        if bcrypt.hashpw(password, self.password) == self.password:
            return True

    def get_id(self):
        return self.key.id()

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid)

    @classmethod
    def by_name(cls, name):
        return cls.query(User.username == name).get()

    @classmethod
    def register(cls, username, password, email=None):
        hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())
        user = User(username=username, password=hashed_pw, email=email)
        return user


class Post(ndb.Model):
    '''
        Post is the model for blog posts
    '''

    title = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    create_date = ndb.DateTimeProperty(auto_now_add=True)
    owner = ndb.KeyProperty(kind=User)
    owner_id = ndb.StringProperty()
    modified_date = ndb.DateTimeProperty(auto_now=True)
    like_count = ndb.IntegerProperty(default=0)
    likes = ndb.StringProperty(repeated=True)

    # shorthand method to get post id
    def get_id(self):
        return self.key.id()

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

    def get_friendly_url(self):
        safe_title = self.title.replace(' ', '_').lower()
        return '%s/%s/' % (str(self.get_id()), safe_title)

    # add a new like to a post
    def like(self, user_id):
        self.like_count += 1
        self.likes.append(str(user_id))
        print(str(user_id) + 'liked the thing')

    # determine if a user has already liked a post
    def already_liked(self, user_id):
        if self.likes.count(str(user_id)) > 0:
            return True

    def is_creator(self, user_id):
        if int(self.owner_id) == int(user_id):
            return True

    def owner_name(self):
        owner = self.owner.get()
        if owner:
            return owner.username

    @classmethod
    def by_id(cls, pid):
        return cls.get_by_id(pid)


class Comment(ndb.Model):
    '''
        Posts can have Comments related to them posted by Users
        As such Comments have two reference properties: user and post

        Probably good to add a modified date in the future...
    '''
    comment = ndb.TextProperty(required=True)
    user = ndb.KeyProperty(
        kind=User, required=True)
    post = ndb.KeyProperty(
        kind=Post, required=True)
    create_date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_comments(cls, post=None):
        if post:
            return cls.query(Comment.post == post.key).fetch()
        else:
            return cls.query().fetch()

    def render(self):
        return self.comment.replace('\n', '<br>')

    def get_id(self):
        return self.key.id()

    def username(self):
        user = self.user.get()
        if user:
            return user.username

    def user_id(self):
        user = self.user.get()
        if user:
            return user.get_id()
