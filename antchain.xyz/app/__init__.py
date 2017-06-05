# ! /usr/bin/env python
# -*- coding: UTF-8 -*-

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from pymongo import MongoClient
from flask_mongoengine import MongoEngine
from flask_mail import Mail
from weixin import Weixin
from config import config
from flask_celery import Celery

bootstrap = Bootstrap()
monment = Moment()
mail = Mail()
moment=Moment()
babel=Babel()
db_me=MongoEngine()
db = MongoClient(connect=False).antchain_mainnet
login_manager=LoginManager()
login_manager.session_protection='strong'
login_manager.login_view='auth.login'
# weixin=Weixin()
celery=Celery()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    # CSRFProtect(app)

    bootstrap.init_app(app)
    monment.init_app(app)
    mail.init_app(app)
    babel.init_app(app)
    db_me.init_app(app)
    login_manager.init_app(app)
    # weixin.init_app(app)
    celery.init_app(app)
    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # from .wx import wx as wx_blueprint
    # app.register_blueprint(wx_blueprint,url_prefix='/wx')

    return app
