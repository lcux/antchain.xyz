#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 5/1/17 10:04 PM
# @Author  : lcux
# @Site    : https://github.com/lcux
# @File    : __init__.py
# @Software: PyCharm

from flask import Blueprint

admin=Blueprint('admin',__name__)

from. import views
