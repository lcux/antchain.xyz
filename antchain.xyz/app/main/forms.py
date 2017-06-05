#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 4/22/17 11:19 PM
# @Author  : lcux
# @Site    : https://github.com/lcux
# @File    : forms.py
# @Software: PyCharm

from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired

class NameForm(FlaskForm):
    name=StringField('what is your name?',validators=[DataRequired()])
    submit=SubmitField('Submit')
