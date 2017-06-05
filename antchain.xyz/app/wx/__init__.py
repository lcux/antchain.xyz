#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 5/14/17 10:47 PM
# @Author  : lcux
# @Site    : https://github.com/lcux
# @File    : __init__.py
# @Software: PyCharm

from flask import Blueprint

wx = Blueprint('wx', __name__)

from . import views, errors
