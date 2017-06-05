#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 4/24/17 10:54 PM
# @Author  : lcux
# @Site    : https://github.com/lcux
# @File    : __init__.py
# @Software: PyCharm

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
