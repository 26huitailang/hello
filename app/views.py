from flask import Flask, flash, request, redirect, render_template, url_for, session, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import login_required, logout_user, current_user
from app import app, github, lm, db
from models import User
from config import ADMIN_ACCOUNT
from datetime import datetime
from forms import EditForm

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    posts = [  # fake array of posts
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html',
                           title='Home',
                           user=user,
                           posts=posts)


@app.route('/login_page')
def login_page():
    return render_template('login.html')


@app.route('/user/<nickname>')
@login_required
def user(nickname):
    # if 'token' in session.keys():
    #     auth = github.get_session(token=session['token'])
    #     resp = auth.get('/user')
    #     if resp.status_code == 200:
    #         user_j = resp.json()
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('login'))
    posts = [
        {'author': user, 'body': 'Test post 1111'},
        {'author': user, 'body': 'Test post 2222'}
    ]
    # print user.avatar_url
    return render_template('user.html',
                           user=user,
                           posts=posts)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)

 
@app.route('/login')
def login():
    redirect_uri = url_for('authorized', next=request.args.get('next') or
                          request.referrer or None, _external=True)
    # print(redirect_uri)
    # More scopes http://developer.github.com/v3/oauth/#scopes
    params = {'redirect_uri': redirect_uri, 'scope': 'user'}
    # print(github.get_authorize_url(**params))
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

    if me['login'] not in  ADMIN_ACCOUNT:
        return redirect(url_for('index'))

    user = User.get_or_create(me['login'], me['name'], me['email'], me['avatar_url'])
 
    session['token'] = auth.access_token
    session['user_id'] = user.id
 
    flash('Login in successful. nickname=%r, avatar_url=%r' % (me['name'], me['avatar_url']))
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))