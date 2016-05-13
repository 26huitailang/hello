#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from config import basedir, QQ_APP_ID, QQ_APP_SECRET
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.config.from_object('config')  # read config and use it
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'index'
oid = OpenID(app, os.path.join(basedir, 'tmp'))
oauth = OAuth(app)

qq = oauth.remote_app('qq',
                      base_url='https://graph.qq.com',
                      request_token_url=None,
                      consumer_key=QQ_APP_ID,
                      consumer_secret=QQ_APP_SECRET,
                      authorize_url='https://graph.qq.com/oauth2.0/authorize',
                      access_token_url='/oauth2.0/token',
                      request_token_params={'scope': 'get_user_info'}
)

if not app.debug and os.environ.get('HEROKU') is None:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('microblog startup')

if os.environ.get('HEROKU') is not None:
    import logging
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('microblog startup')

from app import views, models
