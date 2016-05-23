from app import db, app
from config import WHOOSH_ENABLED, ADMIN_ACCOUNT
from flask.ext.login import UserMixin

enable_search = WHOOSH_ENABLED
if enable_search:
    import flask.ext.whooshalchemy as whooshalchemy

# models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), index=True, unique=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    avatar_url = db.Column(db.String(120))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)

    def __init__(self, login, nickname, email, avatar_url):
        self.login = login
        self.nickname = nickname
        self.email = email
        self.avatar_url = avatar_url

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % self.login

    @staticmethod
    def get_or_create(login, nickname, email, avatar_url):
        user = User.query.filter_by(login=login).first()
        if user is None:
            user = User(login, nickname, email, avatar_url)
            db.session.add(user)
            db.session.commit()
        return user


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)

# if enable_search:
#     whooshalchemy.whoosh_index(app, Post)