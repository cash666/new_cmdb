# -*- coding: utf-8 -*-
# @Time    : 2017/11/30 10:47
# @Author  : caoshuai
# @File    : mail.py
# @Software: PyCharm Community Edition

from app import app,mail
from flask_mail import Mail,Message
from flask import render_template
from threading import Thread

def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

def send_mail(subject,receiver_list,template,**kwargs):
    msg = Message(subject = subject,sender = app.config['FROM_EMAIL'],recipients = receiver_list)
    msg.html = render_template(template + '.html',**kwargs)
    t = Thread(target = send_async_email, args=[app, msg])
    t.start()