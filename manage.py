# -*- coding: utf-8 -*-
# author: notedit

import os
import sys
import socket
import json
import time
import re
import random
#from HTMLParser import HTMLParser
from urllib.parse import urlencode
from urllib.request import urlopen, urlretrieve
from datetime import datetime
from datetime import timedelta

curr_path = os.path.normpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
sys.path.insert(0, curr_path)

from flask import current_app
from flask.ext.script import Manager, prompt, prompt_pass, \
    prompt_bool, prompt_choices
from flask.ext.script import Server

from park import create_app, strutil
from park.strutil import generate_live_user
# from park import configs
from park.configs import APP_CONFIG
from park.extensions import db

import subprocess

from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from werkzeug.security import generate_password_hash, check_password_hash
from park.models.models import CmsUser, User, RecommendPos, \
    Group, Post, Tag, Tagmap, Storage, UserAlias, Video, Game, LiveStream,\
    Report

from park.init_data import init_all


from emitter import Emitter

from utils import generate_base_sitemap, generate_google_sitemap, generate_baidu_sitemap

from sqlalchemy import func
from park.extensions import redis_rank, redis, db

from park.models import backend

from sqlalchemy import func

from park import configs

'''
this is the last chance
'''


if socket.gethostname().startswith('aliyun'):
    app = create_app(configs.ProductionConfig)
elif socket.gethostname().startswith('iZ25p9hiiqvZ') or socket.gethostname().startswith('linode'):
    app = create_app(configs.DevelopmentConfig)
else:
    app = create_app(configs.TestConfig)


#app = create_app(configs.ProductionConfig)
manager = Manager(app)

#socketio = Emitter({'host': 'localhost', 'port': 6379})


@manager.command
def create_all():
    if prompt_bool("Are you sure? You will init your database"):
        db.init_idgenerate()
        db.create_all()
        db.session.commit()


@manager.command
def init_data():
    db.drop_all()
    db.init_idgenerate()
    db.create_all()
    init_all()


@manager.command
def drop_all():
    if prompt_bool("Are you sure? You will lose all your data!"):
        db.drop_all()
        db.session.commit()


@manager.command
def init_redis_rank():

    import random

    users = User.query.limit(100).all()

    for u in users:

        redis_rank.UserHotRank.write(
            u.id,random.randint(200,100000))


@manager.option('-u', '--username', dest='username', default='jazpenn')
@manager.option('-p', '--password', dest='password', default='jia')
@manager.option('-e', '--email', dest='email', default='jazpenn@163.com')
def create_user(username=None, password=None, email=None):
    password = generate_password_hash(password)
    cmsuser = CmsUser(username=username, password=password, email=email)
    db.session.add(cmsuser)
    db.session.commit()
    print('cmsuser %s was added' % username)


# 爬虫  不要乱动
@manager.option('-sn', '--spider_name', dest='spider_name')
def run_spider(spider_name):

    if spider_name not in ["qq", "wdj", "360", "baidu"]:
        print("The spider is not exists.")
        return

    cur_dir = os.path.dirname(__file__)
    spider_path = os.path.join(
        cur_dir, "game_crawl/game_crawl/spiders/%s_spider.py" % spider_name)
    log_path = os.path.join(cur_dir, "game_crawl/game_spider.log")

    run_cmd = ["/usr/local/bin/scrapy", "runspider", "-s", "AUTOTHROTTLE_ENABLED=1", "-s", "LOG_FILE=" + log_path,
               "-s", "LOG_LEVEL=ERROR", spider_path]

    re = subprocess.Popen(run_cmd)

MAX_SITEMAP_COUNT = 10000


@manager.command
def generate_sitemap():

    videos = Video.query.filter(Video.show == True).order_by(
        'date_create desc').limit(MAX_SITEMAP_COUNT)
    new_videos = []
    for each_video in videos:
        each_video.__setattr__("game", '')
        if each_video.game_id:
            try:
                game = Game.query.get(each_video.game_id)
                each_video.__setattr__("game", game.name)
            except Exception as error:
                raise error
        new_videos.append(each_video)

    cur_dir = os.path.dirname(__file__)
    base_sitemap_path = os.path.join(cur_dir, "park/static/sitemap.xml")
    gg_sitemap_path = os.path.join(cur_dir, "park/static/ggsitemap.xml")
    bd_sitemap_path = os.path.join(cur_dir, "park/static/bd_video_sitemap.xml")

    generate_base_sitemap(new_videos, base_sitemap_path)
    generate_google_sitemap(new_videos, gg_sitemap_path)
    generate_baidu_sitemap(new_videos, bd_sitemap_path)


def _fake_request():
    builder = EnvironBuilder(
        method='GET', data={'fake': 'fake'}, environ_base={'REMOTE_ADDR': '127.0.0.1'})
    req = Request(builder.get_environ())
    return req


@manager.command
def give_user_five():

    from park.logutil import insert_user_action

    # 抓取最近一分钟内的 给他伪造了一点播放量
    minutes_ago = datetime.now() - timedelta(minutes=1)

    videos = Video.query.filter(Video.date_create >= minutes_ago).all()

    # 如果粉丝数在 0 - 5  增加  5-10 播放
    # 如果粉丝数在 5 - 20  增加  10 - 20 播放
    # 如果粉丝数在  > 20   增加   15 - 30

    req = _fake_request()
    for vi in videos:
        fcount = backend.get_user_follower_count(vi.creater_id)
        if fcount < 5:
            count = random.randint(5, 10)
        elif fcount >= 5 and fcount < 20:
            count = random.randint(10, 20)
        elif fcount >= 20:
            count = random.randint(15, 30)
        else:
            continue

        vi.play_count += count
        vi.real_play_count += 1

        db.session.commit()

        insert_user_action(
            'watch_video', vi.id, None, req, **{'count': count, '_from': 'web'})


@manager.command
def dump_video_data():

    import csv

    videos = Video.query.filter(Video.show == True).filter(Video.date_create >= '2015-07-06').\
        filter(
            Video.date_create <= '2015-07-13').order_by('date_create asc').all()

    with open('videos.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for vi in videos:
            writer.writerow([vi.title, vi.tags, vi.danmu_count,
                             vi.real_play_count, vi.like_count, vi.comment_count])


@manager.command
def dump_game_data():

    import csv

    res = db.session.query(Game.id, Game.name, Game.package_name, func.count(Video.id).label('total')).\
        join(Video, Game.id == Video.game_id).group_by(
            Game.id).order_by('total desc').all()

    print(res)
    print(len(res))

    with open('games.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for re in res:
            writer.writerow([re[0], re[1], re[2], re[3]])


@manager.command
def create_live():

    from park.models.models import Live
    Live.__table__.drop(bind=db.engine, checkfirst=True)

    Live.__table__.create(bind=db.engine, checkfirst=True)


@manager.command
def init_user_info():

    users = User.query.order_by('date_create desc').limit(300).all()

    i = 0
    for user in users:
        i += 1
        #follower_count = backend.get_user_follower_count(user.id)
        user.follower_count = 1000
        print(user.id)
        if i > 100:
            db.session.commit()
            i = 0
    db.session.commit()


@manager.command
def init_live():

    from park.models.models import Live

    users = User.query.order_by('date_create desc').limit(100).all()

    for u in users:

        for i in range(100):
            live = Live(title='全民枪战实况解说哈哈哈',
                        user_id=u.id,
                        stream_id='',
                        room_id=u.room_id,
                        recommended=True,
                        snapshot='http://tinimage.wan123.tv/27cfb64e8ff611e5b3a600163e000e68.png-tiny',
                        video_url='http://encode.tinvideo.wan123.tv/27cfb64e8ff611e5b3a600163e000e68.mp4',
                        phone_model='iPhone')
            db.session.add(live)
        db.session.commit()


@manager.command
def init_reward():

    from park.models.models import Reward


    Reward.__table__.create(bind=db.engine,checkfirst=True)




#################

@manager.command
def init_charge():

    from park.models.models import Charge, ChargeCategory

    ChargeCategory.__table__.create(bind=db.engine, checkfirst=True)

    for a in range(1, 9):

        cc = ChargeCategory(cost=a*100, count=a*1000)
        db.session.add(cc)

    db.session.commit()

    user_id = 1120012479800280124

    for a in range(100):

        charge = Charge(charge_id='', user_id=user_id,
                        order_no='', cost=200, count=2000,
                        success=True)

        db.session.add(charge)

    db.session.commit()


@manager.command
def init_gift():

    from park.models.models import Gift,Reward


    """
    name introduction  count pic
    """

    Reward.__table__.drop(bind=db.engine,checkfirst=True)

    Gift.__table__.drop(bind=db.engine,checkfirst=True)

    Gift.__table__.create(bind=db.engine,checkfirst=True)



    gift1 = Gift(name='节操',count=10,local_id='jiecao',pic='http://7u2tgb.com2.z0.glb.qiniucdn.com/jiecao.png')

    gift2 = Gift(name='膝盖',count=99,local_id='xigai',pic='http://7u2tgb.com2.z0.glb.qiniucdn.com/xigai.png')
    gift3 = Gift(name='啪啪啪',count=666,local_id='papapa',pic='http://7u2tgb.com2.z0.glb.qiniucdn.com/papapa.png')

    gift4 = Gift(name='抱抱',count=2333,local_id='baobao',pic='http://7u2tgb.com2.z0.glb.qiniucdn.com/baobao.png')

    gift5 = Gift(name='么么哒',count=6666,local_id='memeda',pic='http://7u2tgb.com2.z0.glb.qiniucdn.com/memeda.png')

    gift6 = Gift(name='肥皂',count=9999,local_id='feizao',pic='http://7u2tgb.com2.z0.glb.qiniucdn.com/feizao.png')

    db.session.add_all([gift1,gift2,gift3,gift4,gift5,gift6])

    db.session.commit()


@manager.command
def init_charge_category():

    from park.models.models import ChargeCategory

    """
    title  cost  count
    """

    cc1 = ChargeCategory(title='', cost=200, count=2000)
    cc2 = ChargeCategory(title='', cost=1000, count=10000)
    cc3 = ChargeCategory(title='', cost=2000, count=20000)
    cc4 = ChargeCategory(title='', cost=5000, count=50000)
    cc5 = ChargeCategory(title='', cost=10000, count=100000)
    cc6 = ChargeCategory(title='', cost=20000, count=200000)
    cc7 = ChargeCategory(title='', cost=50000, count=500000)
    cc8 = ChargeCategory(title='', cost=100000, count=1000000)

    db.session.add_all([cc1, cc2, cc3, cc4, cc5, cc6, cc7, cc8])
    db.session.commit()



@manager.command
def init_live():

    from park.models.models import Video, Live


    Live.__table__.drop(bind=db.engine,checkfirst=True)

    Live.__table__.create(bind=db.engine,checkfirst=True)




@manager.command
def import_recommend_video():

    from park.models.models import Video, Live

    videos = Video.query.filter_by(recommended=True).order_by('date_create desc').\
        limit(4000).all()

    for video in videos:

        _video = video.json()

        if not video.encoded_url:
            continue

        live = Live(title=_video['title'],
                    snapshot=_video['video_pic'],
                    video_url=_video['encoded_url'],
                    user_id=_video['creater_id'],
                    room_id=video.creater.room_id,
                    recommended=True,
                    show=True,
                    time=600,
                    play_count=video.play_count,
                    date_create=video.date_create
                    )

        db.session.add(live)

    db.session.commit()


def init_user_range(start,end):

    users = User.query.order_by('date_create asc').\
                limit(10000).offset(start).all()


    i = 0
    for user in users:
        i += 1
        follower_count = backend.get_user_follower_count(user.id)
        following_count = backend.get_user_following_count(user.id)
        user.follower_count = follower_count
        user.following_count = following_count

        if i > 100:
            db.session.commit()
            print('100')
            i = 0
    db.session.commit()



@manager.command
def init_user_info():

    from park.models.models import User

    init_user_range(0,10000)

    print('=' * 100)
    init_user_range(10000,20000)

    print('=' * 100)
    init_user_range(20000,30000)

    print('=' * 100)
    init_user_range(30000,40000)

    print('=' * 100)
    init_user_range(40000,50000)

    print('=' * 100)
    init_user_range(50000,60000)


@manager.command
def modify_gift_info():

    from park.models.models import Gift

    gift1 = Gift.query.filter_by(count=49).first()

    gift1.count = 10

    db.session.commit()


@manager.command
def dump_live_time():

    import csv
    from  datetime import date,datetime,timedelta
    from park.models.models import User,Live

    lives = db.session.query(Live.user_id,func.sum(Live.time).label('live_time')).\
            filter(Live.date_create < date.today()).\
            filter(Live.date_create > str(date.today() - timedelta(days=1))).\
            group_by(Live.user_id).order_by('live_time desc').all()


    with open('live_time.csv','wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',',quoting=csv.QUOTE_MINIMAL)
            for li in lives:
                user = User.query.get(li[0])
                writer.writerow([user.username,user.room_id,str(timedelta(seconds=li[1]))])

                print(user.username,user.room_id,str(timedelta(seconds=li[1])))


@manager.command
def init_redenvelop():

    from park.models.models import Redenvelop

    Redenvelop.__table__.create(bind=db.engine,checkfirst=True)


manager.add_command('runserver', Server())

if __name__ == '__main__':
    app.debug = True
    app.use_debugger = True
    manager.run()
