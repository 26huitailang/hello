#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from .forms import LoginForm
from .models import User
# from oauth import OAuthSignIn
from app import qq

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
@app.route('/index')
# @login_required
def index():
    # user = g.user
    # posts = [  # fake array of posts
    #    {
    #        'author': {'nickname': 'John'},
    #        'body': u'今天三圣乡白鹭湾天气不错！20160508！'
    #    },
    #     {
    #         'author': {'nickname': 'Spiderman'},
    #         'body': 'I\'m the fan of Captain America.'
    #     }
    # ]
    # return render_template('index.html',
    #                         title='',
    #                         user=user,
    #                         posts=posts)
    return redirect(url_for('login'))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/login')
def login():
    return qq.authorize(callback=url_for('qq_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))

@app.route('/login/authorized')
@qq.authorized_handler
def qq_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = qq.get('/me')
    return 'Logged in as id=%s name=%s redirect=%s' % \
        (me.data['id'], me.data['name'], request.args.get('next'))

@qq.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

# @app.route('/login', methods=['GET', 'POST'])
# @oid.loginhandler
# def login():
#     if g.user is not None and g.user.is_authenticated:
#         return redirect(url_for('index'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         session['remember_me'] = form.remember_me.data
#         return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
#     return render_template('login.html',
#                             title=u'登录',
#                             form=form,
#                             providers=app.config['OPENID_PROVIDERS'])

# @oid.after_login
# def after_login(resp):  # The resp argument passed to the after_login function contains information returned by the OpenID provider.
#     if resp.email is None or resp.email == "":
#         flash('Invalid login. Please try again.')
#         return redirect(url_for('login'))
#     user = User.query.filter_by(email=resp.email).first()
#     if user is None:
#         nickname = resp.nickname
#         if nickname is None or nickname == "":
#             nickname = resp.email.split('@')[0]
#         user = User(nickname=nickname, email=resp.email)
#         db.session.add(user)
#         db.session.commit()
#     remember_me = False
#     if 'remember_me' in session:
#         remember_me = session['remember_me']
#         session.pop('remember_me', None)
#     login_user(user, remember = remember_me)
#     return redirect(request.args.get('next') or url_for('index'))

@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html',
                            user=user,
                            posts=posts)

# @app.route('/authorize/<provider>')
# def oauth_authorize(provider):
#     if not current_user.is_anonymous:
#         return redirect(url_for('index'))
#     oauth = OAuthSignIn.get_provider(provider)
#     return oauth.authorize()
#
# @app.route('/callback/<provider>')
# def oauth_callback(provider):
#     if not current_user.is_anonymous():
#         return redirect(url_for('index'))
#     oauth = OAuthSignIn.get_provider(provider)
#     social_id, username, email = oauth.callback()
#     if social_id is None:
#         flash('Authentication failed.')
#         return redirect(url_for('index'))
#     user = User.query.filter_by(social_id=social_id).first()
#     if not user:
#         user = User(social_id=social_id, nickname=username, email=email)
#         db.session.add(user)
#         db.session.commit()
#     login_user(user, True)
#     return redirect(url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))