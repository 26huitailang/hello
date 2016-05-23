from flask.ext.mail import Message
from app import mail, app
from threading import Thread
from config import ADMINS
from flask import render_template


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()


def post_notification(post, user):
    send_email("[Bazinga] %s posts a message!" % post.author.nickname,
               ADMINS[0],
               [user.email],
               render_template("post_email.txt",
                               user=user,
                               post=post),
               render_template("post_email.html",
                               user=user,
                               post=post))