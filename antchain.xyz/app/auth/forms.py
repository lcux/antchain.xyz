#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 4/24/17 10:55 PM
# @Author  : lcux
# @Site    : https://github.com/lcux
# @File    : auth/forms.py
# @Software: PyCharm

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo,InputRequired

from ..models import  User

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(message='请填写您的电子邮件地址！'), Email('请输入正确格式的电子邮件地址！'), Length(min=1, max=64,message='email地址长度必须在6位和64位之间！')])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me?")
    submit = SubmitField("Log In")

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(min=6, max=64)])
    username = StringField("Username", validators=[DataRequired(), Length(min=6, max=64),
        Regexp("^[A-Za-z][A-Za-z0-9_]*$", 0, "Username must have only letters, numbers and uderscores.")])
    password = PasswordField("Password", validators=[DataRequired(),Length(min=6, max=64,message='长度必须在6和64字符之间！')])
    password2 = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password", message="Password must match.")])
    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.objects(email=field.data).first() is not None:
            raise ValidationError("Email already existed.")

    def validate_username(self, field):
        if User.objects(username=field.data).first() is not None:
            raise ValidationError("Username already existed.")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('New Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class ChangeEmailForm(FlaskForm):
    email = StringField('New Email', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')