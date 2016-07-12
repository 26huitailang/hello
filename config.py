# -*- coding: utf-8 -*-

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
# OAUTH_CREDENTIALS = {
#     'qq': {
#         'id': '101312547',
#         'secret': 'cf44c012ba65f5417a298b2991a16bdb'
#     }
# }

QQ_APP_ID = '101312547'
QQ_APP_SECRET = 'cf44c012ba65f5417a298b2991a16bdb'

OPENID_PROVIDERS = [
    {'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    {'name': 'MyOpenID', 'url':'http://huitailang.openid.org.cn/'}
]

ADMIN_ACCOUNT = ['26huitailang']

# mail server settings
MAIL_SERVER = 'smtp.qq.com'
MAIL_PORT = 465
# MAIL_USE_TLS = True
MAIL_USE_SSL = True
MAIL_USERNAME = '50590960'
MAIL_PASSWORD = '' # qq:

#administrator list
ADMINS = ['50590960@qq.com', 'chensijian199182@163.com', '26huitailang@gmail.com']

import os
basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(basedir, 'app.db') +
                               '?check_same_thread=False')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_RECORD_QUERIES = True
WHOOSH_BASE = os.path.join(basedir, 'search.db')

# Whoosh does not work on Heroku
WHOOSH_ENABLED = os.environ.get('HEROKU') is None

# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5

# pagination
POSTS_PER_PAGE = 5

LANGUAGES = {
    'en': 'English',
    'zh_Hans_CN': 'Chinese'
}