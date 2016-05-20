from flask import Flask, flash, request, redirect, render_template, url_for, session, g
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import login_required, logout_user, current_user
from app import app, github, lm, db
from models import User, Post
from config import ADMIN_ACCOUNT, POSTS_PER_PAGE
from datetime import datetime
from forms import EditForm, PostForm
from .emails import post_notification


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
    if 'user_id' in session:
        if session['user_id']:
            user = User.query.get(session['user_id'])
            if user:
                g.user = user
            else:
                del session['user_id']


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def not_found_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user)
        db.session.add(post)
        db.session.commit()
        # flash('Your post is now live!')
        post_notification(post, g.user)
        return redirect(url_for('index'))
    posts = g.user.posts.paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html',
                           title='Home',
                           form=form,
                           posts=posts)


@app.route('/data')
def data():
    # if 'token' in session.keys():
    if session.has_key('token'):
        auth = github.get_session(token=session['token'])
        user_json = auth.get('/gists').json()
        return render_template('data.html',
                               user_json=user_json)
        # if resp.status_code == 200:
        #     user_json = resp.json()
        #     return render_template('data.html',
        #                            user_json=user_json)


@app.route('/login_page')
def login_page():
    return render_template('login.html')


@app.route('/user/<nickname>')
@login_required
def user(nickname):
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
    params = {'redirect_uri': redirect_uri, 'scope': 'user, gist'}
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
                scope='user, gist')

    auth = github.get_auth_session(data=data)
 
    # the "me" response
    me = auth.get('user').json()

    if me['login'] not in  ADMIN_ACCOUNT:
        return redirect(url_for('index'))

    # db.session.commit()
    user = User.get_or_create(me['login'], me['name'], me['email'], me['avatar_url'])
 
    session['token'] = auth.access_token
    session['user_id'] = user.id
 
    # flash('Login in successful. nickname=%r, avatar_url=%r' % (me['name'], me['avatar_url']))
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))