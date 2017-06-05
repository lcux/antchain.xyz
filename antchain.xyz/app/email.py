#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 5/2/17 12:10 AM
# @Author  : lcux
# @Site    : https://github.com/lcux
# @File    : email.py
# @Software: PyCharm

from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail, celery


def send_async_email(to, subject, template, **kwargs):
    msg = Message(current_app.config["XYZ_MAIL_SUBJECT_PREFIX"] + subject,
                  sender=current_app.config["XYZ_MAIL_SENDER"], recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    send_async_email_helper.delay(msg)


@celery.task
def send_async_email_helper(msg):
    with current_app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
