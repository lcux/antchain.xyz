#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 5/14/17 10:47 PM
# @Author  : lcux
# @Site    : https://github.com/lcux
# @File    : views.py
# @Software: PyCharm

from flask import redirect,request,url_for
from . import wx
from .. import weixin
from datetime import datetime,timedelta

wx.add_url_rule("/wx", view_func=weixin.view_func)


@weixin.all
def all(**kwargs):
    """
    监听所有没有更特殊的事件
    """
    return weixin.reply(kwargs['sender'], sender=kwargs['receiver'], content='all')


@weixin.text()
def hello(**kwargs):
    """
    监听所有文本消息
    """
    return "hello too"


@weixin.text("help")
def world(**kwargs):
    """
    监听help消息
    """
    return dict(content="hello world!")


@weixin.subscribe
def subscribe(**kwargs):
    """
    监听订阅消息
    """
    print(kwargs)
    return "欢迎订阅我们的公众号"


@wx.route("/login")
def login():
    """登陆跳转地址"""
    openid = request.cookies.get("openid")
    next = request.args.get("next") or request.referrer or "/",
    if openid:
        return redirect(next)

    callback = url_for("authorized", next=next, _external=True)
    url = weixin.authorize(callback, "snsapi_base")
    return redirect(url)


@wx.route("/authorized")
def authorized():
    """登陆回调函数"""
    code = request.args.get("code")
    if not code:
        return "ERR_INVALID_CODE", 400
    next = request.args.get("next", "/")
    data = weixin.access_token(code)
    openid = data.openid
    resp = redirect(next)
    expires = datetime.now() + timedelta(days=1)
    resp.set_cookie("openid", openid, expires=expires)
    return resp
