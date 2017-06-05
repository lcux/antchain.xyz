#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 4/23/17 12:23 AM
# @Author  : lcux
# @Site    : https://github.com/lcux
# @File    : __init__.py
# @Software: PyCharm

from flask import Blueprint

api=Blueprint('api',__name__)

from . import views,errors
