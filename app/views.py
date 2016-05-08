#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Peter'}  # fake user
    posts = [  # fake array of posts
       {
           'author': {'nickname': 'John'},
           'body': '今天三圣乡天气不错！'
       },
        {
            'author': {'nickname': 'Spiderman'},
            'body': 'I''m the fan of Captain America.'
        }
    ]
    return render_template('index.html',
                            title='',
                            user=user,
                            posts=posts)