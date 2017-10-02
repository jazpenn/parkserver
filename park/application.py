# -*- coding: utf-8 -*-
# author: Jazpenn

import re
import os
import logging
import hmac
import time
import traceback
from datetime import timedelta,datetime

from flask import Flask, Response, request, g, session, jsonify
from flask import make_response
from flask import render_template
from jinja2 import evalcontextfilter, Markup, escape

from park import configs
from park import authutil
from park import strutil

from park.session import RedisSessionInterface
from park.extensions import redis, db, cache, rq, redis_rank,push_stream
from park.models.models import User
from park.models import backend
from park.reutil import RedisRank

from park import admin, apis, views

__all__ = ['create_app']

"""
subinpark
"""

DEFAULT_APP_NAME = 'park'

REGISTER_BLUE_PRINTS = (
    (apis.instance, '/apis'), # app 部分 api
    (views.instance, None),
    (admin.instance, '/admin_')
)


def create_app(config=None, app_name=None):
    if app_name is None:
        app_name = DEFAULT_APP_NAME

    app = Flask(app_name)

    configure_app(app, config)
    configure_db(app)
    configure_cache(app)
    configure_template_filters(app)
    configure_redis(app)
    configure_push_stream(app)
    configure_session(app)
    configure_rq(app)
    configure_blueprints(app)
    configure_logging(app)
    configure_500(app)
    init_redis_rank(app)
    print(app.url_map)

    return app



def configure_app(app, config):
    app.config.from_object(configs.DefaultConfig())

    if config is not None:
        app.config.from_object(config)

    app.config.from_envvar('APP_CONFIG', silent=True)


def configure_session(app):
    app.session_interface = RedisSessionInterface()


def configure_rq(app):
    rq.init_app(app)


def configure_db(app):
    db.init_app(app)


def configure_redis(app):
    redis.init_app(app)


def configure_cache(app):
    cache.init_app(app)


def configure_push_stream(app):
    push_stream.CHAT_SERVER_URL = app.config['CHAT_SERVER_URL']


def init_redis_rank(app):

    UserHotRank = RedisRank(base_redis_key='user_hot_rank', time_delta=timedelta(days=1),\
                        time_strf='%m-%d', expire_time=timedelta(days=38))

    VideoHotRank = RedisRank(base_redis_key='video_hot_rank', time_delta=timedelta(days=1),\
                        time_strf='%m-%d', expire_time=timedelta(days=12))

    UserActivityRank = RedisRank(base_redis_key='user_activity_rank', time_delta=timedelta(days=1),\
                        time_strf='%m-%d', expire_time=timedelta(days=3))

    redis_rank.__setattr__('UserHotRank', UserHotRank)
    redis_rank.__setattr__('VideoHotRank', VideoHotRank)
    redis_rank.__setattr__('UserActivityRank', UserActivityRank)


# register some filter in template here
def configure_template_filters(app):
    _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

    @app.template_filter()
    @evalcontextfilter
    def nl2br(eval_ctx, value):
        # return vlaue
        result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
                              for p in _paragraph_re.split(escape(value)))
        result = result.replace(' ', '&nbsp;')
        if eval_ctx.autoescape:
            result = Markup(result)
        return result

    from park.filters import register_filters

    for name, _filter in register_filters.items():
        app.jinja_env.filters[name] = _filter


def configure_blueprints(app):
    for blue, url_prefix in REGISTER_BLUE_PRINTS:
        app.register_blueprint(blue, url_prefix=url_prefix)


def configure_500(app):

    @app.errorhandler(500)
    def handler_500(error):
        print(datetime.now())
        traceback.print_exc()
        resp = jsonify(err_message=u'服务器出差了,工程师正在遭受鞭笞')
        resp.status_code = 500
        return resp

def configure_logging(app):

    if app.debug:
        return


    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(module)s:%(funcName)s:%(pathname)s:%(lineno)d]')

    debug_log = os.path.join(app.root_path,
                             app.config['DEBUG_LOG'])

    debug_file_handler = \
        logging.handlers.RotatingFileHandler(debug_log,
                            maxBytes=10000000,
                            backupCount=10)

    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(formatter)
    app.logger.addHandler(debug_file_handler)

    error_log = os.path.join(app.root_path,
                             app.config['ERROR_LOG'])

    error_file_handler = \
        logging.handlers.RotatingFileHandler(error_log,
                            maxBytes=10000000,
                            backupCount=10)

    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    app.logger.addHandler(error_file_handler)

    app.logger.info('park start')




