#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect
from app import app
from .forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Peter'}  # fake user
    posts = [  # fake array of posts
       {
           'author': {'nickname': 'John'},
           'body': u'今天三圣乡白鹭湾天气不错！20160508！'
       },
        {
            'author': {'nickname': 'Spiderman'},
            'body': 'I\'m the fan of Captain America.'
        }
    ]
    return render_template('index.html',
                            title='',
                            user=user,
                            posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for OpenID="%s", remember_me=%s' %
              (form.openid.data, str(form.remember_me.data)))
        return redirect('/index')
    return render_template('login.html',
                            title=u'登录',
                            form=form,
                            providers=app.config['OPENID_PROVIDERS'])