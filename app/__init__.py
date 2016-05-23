#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os
from flask.ext.login import LoginManager
from flask.ext.mail import Mail
from flask.ext.openid import OpenID
from flask.ext.babel import Babel
from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
from rauth.service import OAuth2Service
from .momentjs import momentjs
from flask.json import JSONEncoder

app = Flask(__name__)
app.config.from_object('config')  # read config and use it
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login_page'
mail = Mail(app)
babel = Babel(app)
# oid = OpenID(app, os.path.join(basedir, 'tmp'))

# qq = oauth.remote_app('qq',
#                       base_url='https://graph.qq.com',
#                       request_token_url=None,
#                       consumer_key=QQ_APP_ID,
#                       consumer_secret=QQ_APP_SECRET,
#                       authorize_url='https://graph.qq.com/oauth2.0/authorize',
#                       access_token_url='/oauth2.0/token',
#                       request_token_params={'scope': 'get_user_info'}
# )

#  remote version
github = OAuth2Service(
    name='github',
    base_url='https://api.github.com/',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    client_id= '79306c2506b9926d70a9',
    client_secret= 'e5e3ca1ab4106e1defad32f098aa7ccae931ae92'
)


class CustomJSONEncoder(JSONEncoder):
    """This class adds support for lazy translation texts to Flask's
    JSON encoder. This is necessary when flashing translated texts."""
    def default(self, obj):
        from speaklater import is_lazy_string
        if is_lazy_string(obj):
            try:
                return unicode(obj)  # python 2
            except NameError:
                return str(obj)  # python 3
        return super(CustomJSONEncoder, self).default(obj)

app.json_encoder = CustomJSONEncoder

# if not app.debug and os.environ.get('HEROKU') is None:
#     import logging
#     from logging.handlers import RotatingFileHandler
#     file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 1024 * 1024, 10)
#     file_handler.setLevel(logging.INFO)
#     file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
#     app.logger.addHandler(file_handler)
#     app.logger.setLevel(logging.INFO)
#     app.logger.info('microblog startup')

# if os.environ.get('HEROKU') is not None:
#     import logging
#     stream_handler = logging.StreamHandler()
#     app.logger.addHandler(stream_handler)
#     app.logger.setLevel(logging.INFO)
#     app.logger.info('microblog startup')

if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT),
                               'no-reply@' + MAIL_SERVER, ADMINS,
                               'hello failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/hello.log', 'a',
                                       1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('hello startup')

app.jinja_env.globals['momentjs'] = momentjs

from app import views, models
