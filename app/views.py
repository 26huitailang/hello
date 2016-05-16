from flask import Flask, flash, request, redirect, render_template, url_for, session, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import login_required, logout_user, current_user
from app import app, github, lm
from models import User

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/loginpage')
def loginpage():
    return render_template('login.html')

@app.route('/about')
@login_required
def about():
    if 'token' in session.keys():
        auth = github.get_session(token=session['token'])
        resp = auth.get('/user')
        if resp.status_code == 200:
            user = resp.json()
        return render_template('about.html', user=user)
    else:
        return redirect(url_for('login'))
 
 
@app.route('/login')
def login():
    redirect_uri = url_for('authorized', next=request.args.get('next') or
        request.referrer or None, _external=True)
    print(redirect_uri)
    # More scopes http://developer.github.com/v3/oauth/#scopes
    params = {'redirect_uri': redirect_uri, 'scope': 'user'}
    print(github.get_authorize_url(**params))
    return redirect(github.get_authorize_url(**params))


# same path as on application settings page
@app.route('/github/callback')
def authorized():
    # check to make sure the user authorized the request
    if not 'code' in request.args:
        flash('You did not authorize the request')
        return redirect(url_for('index'))
 
    # make a request for the access token credentials using code
    redirect_uri = url_for('authorized', _external=True)
 
    data = dict(code=request.args['code'],
                redirect_uri=redirect_uri,
                scope='user')

    auth = github.get_auth_session(data=data)
 
    # the "me" response
    me = auth.get('user').json()
 
    user = User.get_or_create(me['login'], me['name'], me['email'])
 
    session['token'] = auth.access_token
    session['user_id'] = user.id
 
    flash(me['name'])
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))