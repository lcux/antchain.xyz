#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # IN linux >>export SECRET_KEY=<LAS94ELDJFALxlkdil9dfx0d890fa9>
    # In Windows >> set SECRET_KEY=<LAS94ELDJFALxlkdil9dfx0d890fa9>
    # SECRET_KEY = os.environ.get('SECRET_KEY')
    SECRET_KEY = 'askjdfalss7fs8d7f'

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    XYZ_MAIL_SUBJECT_PREFIX = '[AntChain.XYZ]'
    XYZ_MAIL_SENDER = 'Antchain.xyz Admin <dlclcux@gmail.com>'
    XYZ_ADMIN = os.environ.get('Antchain.xyz_ADMIN')

    BLOCK_PRE_PAGE = 50
    TX_PRE_PAGE = 50
    ADDRESS_PRE_PAGE = 50

    # 微信配置

    # 微信消息
    WEIXIN_TOKEN = ''
    WEIXIN_SENDER = ''
    WEIXIN_EXPIRES_IN = ''

    # 微信登陆
    # 微信公众平台
    WEIXIN_APP_ID = os.environ.get("WEIXIN_APP_ID") or 'wx8f082b09'
    WEIXIN_APP_SECRET = os.environ.get("WEIXIN_APP_SECRET")

    # 微信支付
    # WEIXIN_APP_ID = ''
    WEIXIN_MCH_ID = ''
    WEIXIN_MCH_KEY = ''
    WEIXIN_NOTIFY_URL = ''
    WEIXIN_MCH_KEY_FILE = ''
    WEIXIN_MCH_CERT_FILE = ''

    #资产asset
    ANS_ASSETID = 'c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b'
    ANC_ASSETID = '602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7'

    # BABEL_DEFAULT_LOCALE='zh'

    CELERY_BROKER_URL = "amqp://guest:guest@localhost:5672//"
    # CELERY_BROKER_URL = 'redis://localhost:6379/0'
    # CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'amqp://guest:guest@localhost:5672//'
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_ENABLE_UTC = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    MONGODB_SETTING = {
        'db': 'project1',
        'host': 'mongodb://localhost/antchain_mainnet'
    }


class ProductionConfig(Config):
    MONGODB_SETTINGS = {
        'db': 'project1',
        'host': 'mongodb://localhost/antchain_mainnet'
    }


class TestingConfig(Config):
    MONGODB_SETTING = {
        "db": "antchain_testnet",
        "host": "127.0.0.1",
        "port": 27017
    }


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

LANGUAGES = {'en': 'English',
             'zh': 'Chinese'}
