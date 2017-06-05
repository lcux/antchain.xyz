#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 4/22/17 11:36 PM
# @Author  : lcux
# @Site    : https://github.com/lcux
# @File    : manage.py
# @Software: PyCharm

import os
from app import create_app
from flask_script import Manager

app=create_app('production')
manager=Manager(app)


if __name__=='__main__':
    manager.run()