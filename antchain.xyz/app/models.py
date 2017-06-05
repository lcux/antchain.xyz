#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 5/1/17 9:55 PM
# @Author  : lcux
# @Site    : https://github.com/lcux
# @File    : models.py
# @Software: PyCharm

import hashlib
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db_me,login_manager
from flask import current_app

class User(db_me.Document,UserMixin):
    email = db_me.StringField(required=True)
    username = db_me.StringField(required=True)
    confirmed = db_me.BooleanField(required=True, default=False)
    password_hash = db_me.StringField(required=True, max_length=128)
    member_since=db_me.DateTimeField(required=True,default=datetime.utcnow())
    last_seen=db_me.DateTimeField(required=True,default=datetime.utcnow())
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"confirm": self.email})

    def confirm(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get("confirm") != self.email:
            return False
        self.confirmed = True
        self.save()
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        self.save()
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.objects(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        self.save()
        return True

    def ping(self):
        self.last_seen = datetime.utcnow()
        self.save()

# callback function for flask-login extentsion
from bson.objectid import ObjectId
@login_manager.user_loader
def load_user(user_id):
    return User.objects.get(id=ObjectId(user_id))



