#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 4/22/17 9:57 PM
# @Author  : lcux
# @Site    : https://github.com/lcux
# @File    : __init__.py
# @Software: PyCharm


from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
