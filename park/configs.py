# -*- coding: utf-8 -*-

import datetime
import socket


class DefaultConfig(object):
    DEBUG = False
    SECRET_KEY = 'leyoleyo'
    SESSION_COOKIE_PATH = '/'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_NAME = '_tintin_session'
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(90)
    COOKIE_SALT = 'tintintintin'
    APPLICATION_SECRET = 'tintintintin'
    HOST = 'tintin.tv'
    CONFIG_TYPE = 'default'
    REDIS_HOST = 'localhost'
    CACHE_TYPE = 'redis'

    REDIS_CLASS = 'redis.StrictRedis'
    FORM_API_SECRET = 'NRgFZRfSUR6zcHSeqBXmkb66q4Y='

    VIDEO_ORIGIN_URL = "http://tinvideo.wan123.tv/"
    VIDEO_ENCODED_URL = "http://encode.tinvideo.wan123.tv/"
    VIDEO_PIC_URL = "http://tinimage.wan123.tv/"

    AVATAR_PIC_URL = "http://7xnm2g.com2.z0.glb.qiniucdn.com/"

    UGC_TIME_OUT = 3

    AES_SECRET = 'wan123_tv_aes_secret'

    DEBUG_LOG = 'log/leyo-debug.log'
    ERROR_LOG = 'log/leyo-error.log'

    POSTGRESQL_HOST = 'localhost'
    RETHINKDB_HOST = 'localhost'

    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:password@%s/leyotv' % POSTGRESQL_HOST

    DEV_HOST = '182.92.152.61'

    WATCH_PING_TIMEOUT = 60

    WATCH_REWARD_TIMEOUT = 600


class TestConfig(object):
    CONFIG_TYPE = 'test'
    #SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:password@localhost/leyotv'
    SQLALCHEMY_ECHO = False
    HOST = 'localhost:8080'
    DEBUG = True
    TESTING = True

    CACHE_TYPE = 'redis'

    VIDEO_ORIGIN_URL = "http://tinvideo.wan123.tv/"
    VIDEO_ENCODED_URL = "http://encode.tinvideo.wan123.tv/"
    VIDEO_PIC_URL = "http://tinimage.wan123.tv/"

    HOST_IP = "127.0.0.1"

    #POSTGRESQL_HOST = DefaultConfig.DEV_HOST
    #RETHINKDB_HOST = DefaultConfig.DEV_HOST
    POSTGRESQL_HOST = 'localhost'
    RETHINKDB_HOST = 'localhost'
    REDIS_HOST = 'localhost'

    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:password@%s/leyotv' % POSTGRESQL_HOST

    DAYU_SECRET = '9ce5e0b308c9588c69a040b3ab4e90e4'
    DAYU_APPKEY = '23264310'
    CHAT_SERVER_URL = 'http://182.92.152.61:9080'

class NoteditConfig(object):
    CONFIG_TYPE = 'notedit'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:password@localhost/leyotv'
    SQLALCHEMY_ECHO = False
    HOST = 'localhost:8080'
    DEBUG = True
    TESTING = True

    CACHE_TYPE = 'redis'


class ProductionConfig(object):
    CONFIG_TYPE = 'production'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:password@localhost/leyotv'
    DEBUG = False
    HOST = 'wan123.tv'
    SESSION_COOKIE_NAME = '_wanshua_session'
    SESSION_COOKIE_DOMAIN = '.wanshua.tv'
    SQLALCHEMY_POOL_SIZE = 10
    CACHE_TYPE = 'redis'
    HOST_IP = "115.29.150.249"
    DAYU_SECRET = '9ce5e0b308c9588c69a040b3ab4e90e4'
    DAYU_APPKEY = '23264310'
    DAYU_URL = 'http://gw.api.taobao.com/router/rest'

    CHAT_SERVER_URL = 'http://101.200.144.186'


class DevelopmentConfig(object):
    CONFIG_TYPE = 'development'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:password@localhost/leyotv'
    DEBUG = False
    HOST = '182.92.152.61:8012'
    SESSION_COOKIE_NAME = '_tintin_session'
    # SESSION_COOKIE_DOMAIN = '.tintin.tv'
    SQLALCHEMY_POOL_SIZE = 10
    CACHE_TYPE = 'redis'
    HOST_IP = "182.92.152.61"

    DAYU_SECRET = '9ce5e0b308c9588c69a040b3ab4e90e4'
    DAYU_APPKEY = '23264310'
    DAYU_URL = 'http://gw.api.taobao.com/router/rest'

    CHAT_SERVER_URL = 'http://182.92.152.61:9080'


APP_CONFIG = None


if socket.gethostname().startswith('aliyun'):
    APP_CONFIG = ProductionConfig
elif socket.gethostname().startswith('iZ25p9hiiqvZ') or socket.gethostname().startswith('linode'):
    APP_CONFIG = DevelopmentConfig
else:
    APP_CONFIG = TestConfig

