from app import db, app
from config import WHOOSH_ENABLED
from flask.ext.login import UserMixin

enable_search = WHOOSH_ENABLED
if enable_search:
    import flask.ext.whooshalchemy as whooshalchemy

# models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True)
    git_id = db.Column(db.String(120))

    def __init__(self, login, git_id):
        self.login = login
        self.git_id = git_id

    def __repr__(self):
        return '<User %r>' % self.login

    @staticmethod
    def get_or_create(login, git_id):
        user = User.query.filter_by(login=login).first()
        if user is None:
            user = User(login, git_id)
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