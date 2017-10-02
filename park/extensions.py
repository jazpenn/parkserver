# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.redis import FlaskRedis
from flask.ext.rq import RQ
from flask.ext.cache import Cache
##from influxdb import InfluxDBClient
from park.PushStream import PushStream
from walrus import Database

from .configs import APP_CONFIG

__all__ = ['db', 'redis', 'rq', 'cache','redis_db']

db = SQLAlchemy()
redis = FlaskRedis()
rq = RQ()
cache = Cache()
redis_rank = type('', (), {})()
push_stream = PushStream()
redis_db = Database()

watch_reward_limit = redis_db.rate_limit('watch_reward_limit',limit=10, per=60*60*24)


# influx_client = InfluxDBClient('localhost', 8086, 'root', 'root', 'wan123_influx')
influx_client = None

#import rethinkdb
#rethink_conn = rethinkdb.connect(
#    host='localhost', port=28015, db='park', auth_key='subin')

from celery import Celery
celery = Celery('tasks', broker='redis://localhost:6379/0')

