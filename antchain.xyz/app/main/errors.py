#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 4/22/17 11:02 PM
# @Author  : lcux
# @Site    : https://github.com/lcux
# @File    : errors.py
# @Software: PyCharm

from flask import render_template
from . import main

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
