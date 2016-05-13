from flask import Flask, redirect, url_for, session, request
from flask_oauth import OAuth
from config import QQ_APP_SECRET, QQ_APP_ID
from app import qq, app

@app.route('/')
def index():
    return redirect(url_for('login'))


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
def get_qq_oauth_token():
    return session.get('oauth_token')
