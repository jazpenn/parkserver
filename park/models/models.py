# -*- coding: utf-8 -*-
# author: leeoxiang

import types
import math
import time
import random
import hashlib
import contextlib
import json
import uuid
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy import Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm import create_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import Column, DateTime, Text, Boolean, Sequence, Integer, \
    String, PickleType, MetaData, ForeignKey, UniqueConstraint, Float
from sqlalchemy.dialects.postgresql import ENUM, ARRAY, Any, All, UUID
from sqlalchemy.sql.expression import text
from sqlalchemy.ext.mutable import Mutable
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.sqlalchemy import BaseQuery
from flask import current_app, abort
from park.extensions import db, cache

from park import strutil
from park.filters import img_path

from flask import current_app as app


DATE_FMT = '%Y-%m-%d %H:%M:%S'
DATE_DEFAULT = '2013-05-30 12:00:00'

def format_date(date):
    return date.strftime(DATE_FMT) if date else DATE_DEFAULT

gen_token = lambda: uuid.uuid1().hex

time_stamp = lambda: int(time.time())


def get_time_int():
    return int(time.time())

SIMPLE_USER = ['id', 'username', 'email', 'avatar', 'type', 'introduction']
SIMPLE_FILM = ['id', 'title', 'introduction', 'pic_small', 'director', 'date_create']
SIMPLE_REVIEW = ['id', 'title', 'creater_id', 'content', 'film_id', 'type']
SIMPLE_NOTE = ['id', 'title', 'creater_id', 'content', 'film_id']
SIMPLE_POST = ['id', 'title', 'creater_id', 'content', 'group_id']




GLOBAL_ID_GENERATOR =   '''
drop sequence  if exists  global_id_sequence;
create sequence global_id_sequence;

CREATE OR REPLACE FUNCTION id_generator(OUT result bigint) AS $$
DECLARE
    our_epoch bigint := 1314220021721;
    seq_id bigint;
    now_millis bigint;
    -- the id of this DB shard, must be set for each
    -- schema shard you have - you could pass this as a parameter too
    shard_id int := 1;
BEGIN
    SELECT nextval('global_id_sequence') % 1024 INTO seq_id;

    SELECT FLOOR(EXTRACT(EPOCH FROM clock_timestamp()) * 1000) INTO now_millis;
    result := (now_millis - our_epoch) << 23;
    result := result | (shard_id << 10);
    result := result | (seq_id);
END;
$$ LANGUAGE PLPGSQL;
'''

def init_idgenerate():

    db.session.execute(text(GLOBAL_ID_GENERATOR))
    db.session.commit()

db.init_idgenerate = init_idgenerate


room_sequence = Sequence('room_id_seq',increment=1)

#  room_sequence.next_value()

class UserQuery(BaseQuery):

    def simple(self, user_id):

        ret = db.session.query(User.id, User.username, User.email, User.avatar,
                               User.type, User.introduction).filter(User.id == user_id).first()

        if ret is None:
            abort(404)

        _dict = dict(zip(SIMPLE_USER, ret))

        return _dict

TEST_URL_PREFIX = 'http://test.tintin.tv/'

class User(db.Model):
    __tablename__ = 'user_info'
    query_class = UserQuery

    id = db.Column(db.BigInteger,server_default=text('id_generator()'),primary_key=True)
    username = db.Column(db.Unicode(50), unique=True, nullable=False)
    nickname = db.Column(db.String(50))
    password = db.Column(db.String(100))
    avatar = db.Column(db.String(255))
    gender = db.Column(db.Boolean,default=True)  # True 女 | False 男 | None 保密
    status = db.Column(db.String(10), default='normal')  # normal  noauth  blocked
    type = db.Column(db.String(20), default='normal')  # 普通用户和认证过的 normal   certificated
    introduction = db.Column(db.Unicode(500), default=u'')
    recommended = db.Column(db.Boolean, default=False)
    date_create = db.Column(db.DateTime, default=datetime.now)
    date_update = db.Column(db.DateTime, default=datetime.now)

    qq = db.Column(db.String(50))
    email = db.Column(db.String(50))
    new_gender = db.Column(db.SmallInteger, default=0)
    phone_number = db.Column(db.String(50))

    token = db.Column(db.String(50), default=gen_token)  # 仅限于移动端

    accept_push = db.Column(db.Boolean, default=True)

    exp_value = db.Column(db.Integer, default=0) # 经验值

    balance = db.Column(db.Float,default=0)

    cny_balance = db.Column(db.Float,default=0)

    wsb_balance = db.Column(db.Float,default=0)

    # 为直播添加的字段

    board = db.Column(db.Text(),default='')

    live_status = db.Column(db.String(20))

    room_id = db.Column(db.Integer,Sequence('room_id_seq',increment=1))

    stream_id = db.Column(db.String(80))

    live_id = db.Column(db.BigInteger)

    #

    follower_count = db.Column(db.Integer,default=0)
    following_count = db.Column(db.Integer,default=0)

    tasks = relationship('UserTask', backref="user")

    @hybrid_property
    def uid(self):
        return strutil.b57encode(self.id) if self.id else None

    # 经验算等级 1:5, 2:15, 3~:math.sqrt(self.exp_value/15-1.75)+2.5
    @hybrid_property
    def level(self):
        if self.exp_value<5:
            return 1
        elif self.exp_value<15:
            return 2
        elif self.exp_value<30:
            return 3
        return int(math.sqrt(self.exp_value/15-1.75)+3.5)

    # 等级算经验 1:5, 2:15, 3~:30 + 15*(level-2)*(level-3)
    @staticmethod
    def level_exp(level):
        if level==1:
            return 5
        elif level==2:
            return 15
        return 30 + 15*(level-2)*(level-3)

    @staticmethod
    def auth(phone,password):

        ua = db.session.query(UserAlias).filter(UserAlias.open_id == phone).first()
        if ua:
            # auth =  True  if hashlib.md5(password).hexdigest() ==  user.password else False
            auth = True if check_password_hash(ua.password, password) else False
        else:
            auth = False
        return ua, auth

    def generate_room_id(self):

        room_id = db.session.execute(room_sequence)

        print(room_id)

        self.room_id = room_id

        db.session.commit()

        print(db.session.execute(text('select id_generator()')).scalar())


    def json(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'username': self.username,
            'nickname': self.nickname,
            'avatar': self.avatar if self.avatar else 'http://7u2tgb.com2.z0.glb.qiniucdn.com/avatar_default.png',
            'status': self.status,
            'gender': self.gender,
            'type': self.type,
            'recommended': self.recommended,
            'introduction': self.introduction,
            'date_create': format_date(self.date_create),
            'date_update': format_date(self.date_update),
            'email': self.email,
            'new_gender': self.new_gender,
            'qq': self.qq,
            'phone_number': self.phone_number,
            'accept_push': self.accept_push,
            'exp_value': self.exp_value,
            'level': self.level,
            'balance':self.balance,

            'board':self.board,
            'live_status':self.live_status,
            'room_id':self.room_id,
            'follower_count':self.follower_count,
            'following_count':self.following_count
        }

    def passhash(self, password):
        # self.password  = hashlib.md5(password).hexdigest()
        self.password = generate_password_hash(password)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.id)


class VideoQuery(BaseQuery):
    def xxxx(self):
        pass

class VideoCache(db.Model):
    __tablename__ = 'video_cache'

    id = db.Column(db.BigInteger,server_default=text('id_generator()'),primary_key=True)

    title = db.Column(db.String(255), nullable=False)

    introduction = db.Column(db.Text(),default='')

    key = db.Column(db.String(100), unique=True)

    video_pic = db.Column(db.String(255), default='')

    origin_url = db.Column(db.String(255))

    encoded_url = db.Column(db.String(255))

    status = db.Column(db.Integer, default=2) # 1 正常(可以访问) 2 正在处理 3 处理失败

    creater_id = db.Column(db.BigInteger, ForeignKey('user_info.id'), index=True, nullable=False)

    creater = relationship('User', uselist=False)

    date_create = db.Column(db.DateTime, default=datetime.now)

    game_id = db.Column(db.Integer)

    tags = db.Column(db.String(100))

    @hybrid_property
    def uid(self):
        return strutil.b57encode(self.id) if self.id else None

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'introduction': self.introduction,
            'key': self.key,
            'origin_url': self.origin_url,
            'encoded_url': self.encoded_url,
            'creater_id': self.creater_id,
            'status': self.status,
            'game_id': self.game_id,
            'tags': self.tags
        }

class Video(db.Model):
    __tablename__ = 'video'
    query_class = VideoQuery

    id = db.Column(db.BigInteger,server_default=text('id_generator()'),primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    introduction = db.Column(db.Text(),default='')
    video_pic = db.Column(db.String(255), default='')
    creater_id = db.Column(db.BigInteger, ForeignKey('user_info.id'), index=True, nullable=False)
    key = db.Column(db.String(100), unique=True)
    url = db.Column(db.String(255))
    origin_url = db.Column(db.String(255))
    encoded_url = db.Column(db.String(255))
    play_count = db.Column(db.Integer, default=0)
    real_play_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    recommended = db.Column(db.Boolean, default=False)
    is_banner = db.Column(db.Boolean, default=False)
    rate = db.Column(db.Float,default=0)
    show = db.Column(db.Boolean, default=True)
    time = db.Column(db.Integer, default=0)
    width = db.Column(db.Integer, default=0)
    height = db.Column(db.Integer, default=0)
    game_id = db.Column(db.Integer)
    channel_id = db.Column(db.BigInteger, ForeignKey('channel.id'), index=True)

    type = db.Column(db.Integer, default=0)  # 2 一般用户上传  3 评测  4 攻略  5  动作   6 竞速  7 射击   8 休闲  and more

    status = db.Column(db.Integer, default=1) # 1 正常(可以访问) 2 正在处理 3 处理失败
    available = db.Column(db.Boolean, default=False)

    date_create = db.Column(db.DateTime, default=datetime.now)
    date_update = db.Column(db.DateTime, default=datetime.now)

    creater = relationship('User', uselist=False)
    channel = relationship('Channel', uselist=False)

    tag_maps = relationship('Tagmap')

    @hybrid_property
    def uid(self):
        return strutil.b57encode(self.id) if self.id else None

    @hybrid_property
    def tags(self):
        return [each.tag for each in self.tag_maps]

    @hybrid_property
    def danmu_count(self):
        return Danmu.query.filter_by(post_id=self.id).count() if self.id else 0

    def json(self, width_creater=None):
        return {
            'id': self.id,
            'uid': self.uid,
            'title': self.title,
            'introduction': self.introduction,
            'video_pic': img_path(self.video_pic) if self.video_pic else "",
            'creater_id': self.creater_id,
            'user': width_creater and self.creater.json(),
            'channel_id': self.channel_id,
            'url': self.url,
            'origin_url': app.config["VIDEO_ORIGIN_URL"] + str(self.origin_url),
            'encoded_url': app.config["VIDEO_ORIGIN_URL"] + str(self.origin_url) if self.encoded_url is None else \
                            app.config["VIDEO_ENCODED_URL"] + self.encoded_url,
            'play_count': self.play_count,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'recommended': self.recommended,
            'is_banner': self.is_banner,
            'rate': self.rate,
            'show': self.show,
            'game_id': self.game_id,
            'type': self.type,
            'status': self.status,
            'available': self.available,
            'date_create': format_date(self.date_create),
            'date_update': format_date(self.date_update),
            'time': self.time
        }

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.id)


class LiveStream(db.Model):

    """
    房间信息
    """
    __tablename__ = 'live_stream'

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.BigInteger,ForeignKey('user_info.id'))
    stream_id = db.Column(db.String(100))
    date_create = db.Column(db.DateTime,default=datetime.now)
    board = db.Column(db.String(1000))


    title = db.Column(db.String(200))
    game = db.Column(db.String(100))
    phone_modol = db.Column(db.String(50))
    status = db.Column(String(20)) #  多种状态

    user = relationship('User', uselist=False)

    @hybrid_property
    def uid(self):
        return strutil.b57encode(self.user_id) if self.user_id else None



    def json(self):
        return {
                'id':self.id,
                'user_id':self.user_id,
                'uid':self.uid,
                'board':self.board,
                'title':self.title,
                'game':self.game,
                'phone_modol':self.phone_modol,
                'status':self.status
                }


class Live(db.Model):


    """
    单个直播

    """
    __tablename__ = 'live'

    id = db.Column(db.BigInteger,server_default=text('id_generator()'),primary_key=True)
    title = db.Column(db.String(100))
    game_id = db.Column(db.Integer)
    user_id = db.Column(db.BigInteger,ForeignKey('user_info.id'),nullable=False,)
    room_id = db.Column(db.Integer,nullable=False)
    stream_id = db.Column(db.String(100),index=True)
    time = db.Column(db.Integer,default=0)
    snapshot = db.Column(db.String(300))
    video_url = db.Column(db.String(300))
    show = db.Column(db.Boolean,default=False)
    recommended = db.Column(db.Boolean,default=False)
    status = db.Column(db.String(20),default='disconnected')
    phone_model = db.Column(db.String(50))
    reply_count = db.Column(db.Integer,default=0)
    play_count = db.Column(db.Integer,default=0)
    real_play_count = db.Column(db.Integer,default=0)
    live_user_count = db.Column(db.Integer,default=3)
    date_create = db.Column(db.DateTime,default=datetime.now)

    tag_id = db.Column(db.Integer,index=True)

    date_start = db.Column(db.Integer,default=time_stamp)
    date_end = db.Column(db.Integer,default=time_stamp)

    user = relationship('User',uselist=False)

    @hybrid_property
    def uid(self):
        return strutil.b57encode(self.id) if self.id else None



    def json(self):

        return {
                'id':self.id,
                'uid':self.uid,
                'title':self.title,
                'game_id':self.game_id,
                'user_id':self.user_id,
                'room_id':self.room_id,
                'stream_id':self.stream_id,
                'time':self.time,
                'snapshot':self.snapshot if not self.snapshot else self.snapshot + '?imageView/2/w/300',
                'recommended':self.recommended,
                'video_url':self.video_url,
                'status':self.status,
                'phone_model':self.phone_model,
                'reply_count':self.reply_count,
                'play_count':self.play_count,
                'live_user_count':self.live_user_count,
                'date_create':format_date(self.date_create)
                }




class Redenvelop(db.Model):

    __tablename__ = 'redenvelop'

    id = Column(Integer,primary_key=True)
    user_id = Column(db.BigInteger,index=True,nullable=False)
    room_id = Column(Integer,nullable=False)
    total_people = Column(Integer,nullable=False)
    total_wsb = Column(Float,nullable=False)
    description = Column(String(300))
    date_create = Column(DateTime,default=datetime.now)

    def json(self):
        return {
                'id':self.id,
                'user_id':self.user_id,
                'total_people':self.total_people,
                'total_wsb':self.total_wsb,
                'description':self.description,
                'date_create':format_date(self.date_create)
                }



class Game(db.Model):
    __tablename__ = 'game'

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    package_name = Column(String(128) , index=True, nullable=False, unique=True)
    apk_mesg = Column(Text)
    game_pic = Column(String(255))
    game_type = Column(Integer, default=1)
    view_count = Column(Integer, default=0)
    rate = Column(Float, default=10)
    show = Column(Boolean, default=True)
    ios_url = Column(String(255))
    android_url = Column(String(255))
    description = Column(Text)
    date_update = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'package_name': self.package_name,
            'apk_mesg': self.apk_mesg,
            'game_pic': self.game_pic,
            'game_type': self.game_type,
            'view_count': self.view_count,
            'rate': self.rate,
            'show': self.show,
            'ios_url': self.ios_url,
            'android_url': self.android_url,
            'description': self.description,
            'date_update': format_date(self.date_update)
        }


class Rating(db.Model):
    __tablename__ = 'rating'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.BigInteger, nullable=False)
    user_id = db.Column(db.BigInteger, nullable=False)
    rate = db.Column(Float())
    date_create = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint('user_id', 'video_id'),
    )

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.id)


# for 专题
class Channel(db.Model):
    __tablename__ = 'channel'

    id = db.Column(Integer, primary_key=True)
    channel_name = db.Column(String(80))
    pic_url = db.Column(String(500))
    show = db.Column(Boolean, default=True)
    #is_channel = db.Column(Boolean)
    type = db.Column(String(20))  #  user   web
    relating_info = db.Column(String(500))
    order = db.Column(Integer, default=0)
    date_create = db.Column(db.DateTime, default=datetime.now)
    is_banner = db.Column(Boolean, default=False)
    game_id = db.Column(db.Integer, default=0)

    def json(self):
        return {
            'id': self.id,
            'channel_name': self.channel_name,
            'pic_url': img_path(self.pic_url) if self.pic_url else "",
            'show': self.show,
            #'is_channel': self.is_channel,
            'type': self.type,
            'relating_info': self.relating_info,
            'order': self.order,
            'date_create': str(self.date_create),
            'is_banner': self.is_banner,
            'game_id': self.game_id
        }


class PostQuery(BaseQuery):
    def get_hot_post(self):
        date_limit = datetime.now() + timedelta(days=-2)
        res = db.session.query(Reply.post_id, func.count(Reply.id).label('total')). \
            filter(Reply.group_id != -1).filter(Reply.date_create > date_limit). \
            group_by(Reply.post_id).order_by('total desc').limit(10).all()
        print(res)
        if not res: return []

        hot_post_ids = [r[0] for r in res]

        hot_posts = self.filter(Post.id.in_(hot_post_ids)).all()
        return hot_posts


    def simple(self, post_id):

        ret = db.session.query(Post.id, Post.title, Post.creater_id, Post.content,
                               Post.group_id).filter(Post.id == post_id).first()

        if ret is None:
            abort(404)

        _dict = dict(zip(SIMPLE_POST, ret))

        return _dict


class Post(db.Model):
    """table for小组帖子"""
    __tablename__ = 'post'
    query_class = PostQuery

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    creater_id = db.Column(db.BigInteger, ForeignKey('user_info.id'), index=True, nullable=False)
    content = db.Column(db.Text())
    pic_small = db.Column(db.String(255))
    pic_big = db.Column(db.String(255))
    group_id = db.Column(db.Integer, ForeignKey('groups.id'), nullable=False)
    film_id = db.Column(db.Integer)
    show = db.Column(db.Boolean, default=True)
    recommended = db.Column(db.Boolean)
    comment_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    date_create = db.Column(db.DateTime, default=datetime.now)  # 创建时间
    date_update = db.Column(db.DateTime, default=datetime.now)  # 最后更新时间 比如最后回复 评论以后要更新一下这个字段
    date_modify = db.Column(db.DateTime, default=datetime.now)

    creater = relationship('User', uselist=False)
    group = relationship('Group', uselist=False)

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'creater_id': self.creater_id,
            'content': self.content,
            'pic_small': self.pic_small,
            'pic_big': self.pic_big,
            'group_id': self.group_id,
            'show': self.show,
            'recommended': self.recommended,
            'date_create': format_date(self.date_create),
            'date_update': format_date(self.date_update),
            'date_modify': format_date(self.date_modify)
        }

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.id)


class ReplyQuery(BaseQuery):
    def xxx(self):
        pass


class Reply(db.Model):
    __tablename__ = 'reply'
    query_class = ReplyQuery

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, default=-1)
    reply_type = db.Column(db.String(20))  # video  post
    parent_id = db.Column(db.Integer, db.ForeignKey('reply.id', ondelete='CASCADE'))
    post_id = db.Column(db.BigInteger, index=True, nullable=False)
    content = db.Column(db.Text)
    creater_id = db.Column(db.BigInteger, db.ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    date_create = db.Column(db.DateTime, default=datetime.now)

    #  for danmu
    time = db.Column(db.Float,default=1.0)
    danmu_type = db.Column(db.Integer,default=1)  # 6从左到右  1从右到左  5顶端固定   4底端固定  7高级弹幕 8脚本弹幕
    text_size = db.Column(db.Float,default=20.0)
    color = db.Column(db.Integer,default=0)
    timestamp = db.Column(db.Integer,default=time_stamp)
    pool_type = db.Column(db.Integer,default=1)
    user_hash = db.Column(db.Integer,default=1)

    creater = db.relation(User, innerjoin=True, lazy="joined")
    parent = db.relation('Reply', remote_side=[id])



    def json(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'reply_type': self.reply_type,
            'parent_id': self.parent_id,
            'post_id': self.post_id,
            'content': self.content,
            'creater_id': self.creater_id,
            'date_create': format_date(self.date_create),
            'time':self.time,
            'danmu_type':self.danmu_type,
            'text_size':self.text_size,
            'color':self.color,
            'timestamp':self.timestamp,
            'pool_type':self.pool_type,
            'user_hash':self.user_hash
        }

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.id)


class Danmu(db.Model):
    __tablename__ = 'danmu'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, default=-1)
    reply_type = db.Column(db.String(20))  # video  post
    parent_id = db.Column(db.Integer)
    post_id = db.Column(db.BigInteger, index=True, nullable=False)
    content = db.Column(db.Text)
    creater_id = db.Column(db.BigInteger, db.ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    date_create = db.Column(db.DateTime, default=datetime.now)

    #  for danmu
    time = db.Column(db.Float,default=1.0)
    danmu_type = db.Column(db.Integer,default=1)  # 6从左到右  1从右到左  5顶端固定   4底端固定  7高级弹幕 8脚本弹幕
    text_size = db.Column(db.Float,default=20.0)
    color = db.Column(db.Integer,default=0)
    timestamp = db.Column(db.Integer,default=time_stamp)
    pool_type = db.Column(db.Integer,default=1)
    user_hash = db.Column(db.Integer,default=1)

    creater = db.relation(User, innerjoin=True, lazy="joined")



    def json(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'reply_type': self.reply_type,
            'parent_id': self.parent_id,
            'post_id': self.post_id,
            'content': self.content,
            'creater_id': self.creater_id,
            'date_create': format_date(self.date_create),
            'time':self.time,
            'danmu_type':self.danmu_type,
            'text_size':self.text_size,
            'color':self.color,
            'timestamp':self.timestamp,
            'pool_type':self.pool_type,
            'user_hash':self.user_hash
        }

    def danmu_json(self):
        return {
            "mode": self.danmu_type,
            "text": self.content,
            "stime": self.time,
            "size": self.text_size,
            "color": self.color,
            "duration": 6000
        }

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.id)



class UserAlias(db.Model):
    """新浪微博登陆用"""
    __tablename__ = 'user_alias'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger)  #  用户id
    open_id = db.Column(db.String(100), index=True)  # 第三方网站用户id
    access_token = db.Column(db.String(100))
    type = db.Column(db.String(20))  # 第三方网站类型 weibo or  qq  or wechat  or password
    password = db.Column(db.String(100))
    date_create = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint('user_id', 'type'),
        UniqueConstraint('open_id', 'type')
    )

    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'open_id': self.open_id,
            'access_token': self.access_token,
            'type': self.type,
            'date_create': self.date_create,
        }

class GroupQuery(BaseQuery):
    def get_all_group(self):
        return self.all()


class Group(db.Model):
    __tablename__ = 'groups'
    query_class = GroupQuery

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    pic_small = db.Column(db.String(255))
    pic_big = db.Column(db.String(255))
    abstract = db.Column(db.String(255))
    introduction = db.Column(db.Text())
    creater_id = db.Column(db.Integer)
    post_count = db.Column(db.Integer, default=0)
    date_create = db.Column(db.DateTime, default=datetime.now)
    date_update = db.Column(db.DateTime, default=datetime.now)


    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'pic_small': self.pic_small,
            'pic_big': self.pic_big,
            'abstract': self.abstract,
            'introduction': self.introduction,
            'creater_id': self.creater_id,
            'post_count': self.post_count,
            'date_create': format_date(self.date_create),
            'date_update': format_date(self.date_update)
        }

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.id)


class Follow(db.Model):
    """follow 关系"""
    __tablename__ = 'follow'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, index=True)
    user_id_to = db.Column(db.BigInteger, index=True)
    date_create = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint('user_id', 'user_id_to'),
    )


class Storage(db.Model):
    __tablename__ = 'storage'

    id = db.Column(db.Integer, primary_key=True)
    md5 = db.Column(db.String(80))
    size = db.Column(db.Integer)


class CmsUser(db.Model):
    __tablename__ = 'cms_user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(255))
    date_create = db.Column(db.DateTime, default=datetime.now)


class RecommendPosQuery(BaseQuery):
    """docstring for RecommendPosQuery"""

    def get_value(self, name):
        pos = self.filter_by(name=name).first()

        return None if pos is None else json.loads(pos.content)


class RecommendPos(db.Model):
    __tablename__ = 'recommend_pos'
    query_class = RecommendPosQuery

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    #type_id = db.Column(db.Integer)
    content = db.Column(db.Text)


class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, index=True)
    type = db.Column(String(20))
    pic_url = db.Column(String(500))
    recommended = db.Column(db.Boolean, default=False)
    show = db.Column(db.Boolean, default=True)
    introduction = db.Column(db.Text)
    date_create = db.Column(db.DateTime, default=datetime.now)

    order = db.Column(Integer, default=0)

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'introduction': self.introduction,
            'type': self.type,
            'pic_url': img_path(self.pic_url) if self.pic_url else "",
            'date_create': self.date_create
        }

    def __repr__(self):
        return "%s" % self.name


class Tagmap(db.Model):
    __tablename__ = 'tag_map'

    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.BigInteger, ForeignKey('tag.id'), index=True)
    #content_id = db.Column(db.BigInteger, index=True)
    video_id = db.Column(db.BigInteger, ForeignKey('video.id'), index=True)

    tag = relationship('Tag', uselist=False)

    __table_args__ = (
        UniqueConstraint('tag_id', 'video_id'),
    )

class ActionQuery(BaseQuery):
    def xxx(self):
        pass


class Action(db.Model):
    __tablename__ = 'action'
    query_class = ActionQuery

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, index=True, nullable=False)
    action_type = db.Column(db.String(20), index=True)
    content_id = db.Column(db.BigInteger, nullable=False)
    attach_id = db.Column(db.BigInteger)  # 如果需要多个id的时候  attach_id 放这个id
    group_id = db.Column(db.BigInteger)
    extra = db.Column(db.String(1024))
    date_create = db.Column(db.DateTime, default=datetime.now, index=True)


    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'attach_id': self.attach_id,
            'action_type': self.action_type,
            'content_id': self.content_id,
            'group_id': self.group_id,
            'extra': self.extra,
            'date_create': format_date(self.date_create)
        }


"""
notify_type


'follow_user'
'reply_video'
'like_video'
'reply_reply'
'system'
"""


class NotifyQuery(BaseQuery):
    def xxx(self):
        pass


class Notify(db.Model):
    __tablename__ = 'notify'
    query_class = NotifyQuery

    id = db.Column(db.Integer, primary_key=True)
    user_to = db.Column(db.BigInteger, index=True, nullable=False)
    notify_type = db.Column(db.String(20), index=True)
    content_id = db.Column(db.BigInteger, index=True)
    is_readed = db.Column(db.Boolean, default=False, index=True)
    date_last_update = db.Column(db.DateTime, default=datetime.now)
    extra = db.Column(db.Text())
    user_from = db.Column(db.BigInteger)
    reply_id = db.Column(db.Integer)
    date_create = db.Column(db.DateTime, default=datetime.now, index=True)


    def json(self):
        return {
            'id': self.id,
            'user_to': self.user_to,
            'notify_type': self.notify_type,
            'content_id': self.content_id,
            'is_readed': self.is_readed,
            'date_create': format_date(self.date_create),
            'date_last_update': format_date(self.date_last_update),
            'user_from':self.user_from,
            'reply_id':self.reply_id
        }

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.id)


class Watch(db.Model):
    __tablename__ = 'watch'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.BigInteger, index=True)
    user_id = db.Column(db.BigInteger, index=True)



    __table_args__ = (
        UniqueConstraint('user_id', 'video_id'),
    )


class Message(db.Model):
    """ 留言板 """
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    # user_id 写给 user_id_to
    user_id = db.Column(db.BigInteger, ForeignKey('user_info.id'), nullable=False)
    user_id_to = db.Column(db.BigInteger, index=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('message.id', ondelete='CASCADE'))
    content = db.Column(db.Text())

    date_create = db.Column(db.DateTime, default=datetime.now)

    # 写的那个user
    user = relationship('User', uselist=False)
    parent = db.relation('Message', remote_side=[id])

    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_id_to': self.user_id_to,
            'content': self.content,
            'parent_id': self.parent_id,
            'date_create': format_date(self.date_create)}


    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.id)


# 用户喜欢的 用来存放喜欢
class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    content_type = db.Column(db.String(20), index=True)  #  film or  something other
    content_id = db.Column(db.BigInteger, nullable=False, index=True)

    date_create = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint('user_id', 'content_id', 'content_type'),
    )

    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_type': self.content_type,
            'content_id': self.content_id
        }



# 用来存放搜藏
class Collect(db.Model):
    __tablename__ = 'collect'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    content_type = db.Column(db.String(20), index=True)  #  film or  something other
    content_id = db.Column(db.BigInteger, nullable=False, index=True)

    date_create = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint('user_id', 'content_id', 'content_type'),
    )

    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_type': self.content_type,
            'content_id': self.content_id
        }


class WatchHistory(db.Model):

    __tablename__ = 'watch_history'

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    video_id = db.Column(db.BigInteger,ForeignKey('video.id'),nullable=False)
    stop_time = db.Column(db.Integer)

    deleted = db.Column(db.Boolean,default=False)
    date_create = db.Column(db.DateTime, default=datetime.now)

    video = relationship('Video', uselist=False)

    def json(self):

        return {'id':self.id,
                'user_id':self.user_id,
                'video_id':self.video_id,
                'stop_time':self.stop_time,
                'date_create':format_date(self.date_create)}

class Version(db.Model):
    __tablename__ = 'version'

    id = db.Column(db.Integer, Sequence('version_id_seq',increment=1),primary_key=True)
    version_name = db.Column(db.String(255), unique=True)
    version_type = db.Column(db.Integer, default=0)
    version_log = db.Column(db.Text(), default="")
    version_url = db.Column(db.Text(), default="")
    version_date = db.Column(db.DateTime, default=datetime.now)

    def json(self):
        return {
            'id': self.id,
            'version_name': self.version_name,
            'version_type': self.version_type,
            'version_log': self.version_log,
            'version_url': self.version_url,
            'version_date': self.version_date
        }

class Vote(db.Model):
    __tablename__ = 'vote'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger)
    video_id = db.Column(db.BigInteger)
    type = db.Column(db.String(20))  # up or down

    __table_args__ = (
        UniqueConstraint('user_id', 'video_id'),
    )


class CertifiApply(db.Model):
    __tablename__ = 'certifi_apply'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger)
    realname = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(50))
    organization = db.Column(db.String(500))
    contact = db.Column(db.String(500))

    date_create = db.Column(db.DateTime, default=datetime.now)


class UserToken(db.Model):
    __tablename__ = 'user_token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger)
    atype = db.Column(db.String(20))  # 'signup' 'find_password'
    token = db.Column(db.String(255), unique=True)
    date_create = db.Column(db.DateTime, default=datetime.now)


class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    content = db.Column(db.Text())

    __table_args__ = (
        UniqueConstraint('email', 'content'),
    )



class Install(db.Model):

    __tablename__ = 'install'

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.BigInteger,db.ForeignKey(User.id),index=True)
    version = db.Column(db.String(20))
    badge = db.Column(db.Integer,default=0)
    device_token = db.Column(db.String(100),index=True)
    device_type = db.Column(db.String(20))
    date_create = db.Column(db.DateTime,default=datetime.now)


    def json(self):

        return dict(id=self.id,
                    user_id=self.user_id,
                    version=self.version,
                    badge=self.badge,
                    device_token=self.device_token,
                    device_type=self.device_type)


class UserTask(db.Model):

    __tablename__ = 'user_task'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.BigInteger,db.ForeignKey(User.id),index=True)
    type = db.Column(db.String(20), default='one_off') # daily one_off
    exp_value = db.Column(db.Integer,default=0)
    aim_count = db.Column(db.Integer,default=0)
    cur_count = db.Column(db.Integer,default=0)
    is_received = db.Column(db.Boolean,default=False)

    date_done = db.Column(db.DateTime,default=datetime.now)
    date_update = db.Column(db.DateTime,default=datetime.now, onupdate=datetime.now)

    __table_args__ = (
        UniqueConstraint('name', 'user_id'),
    )

    @hybrid_property
    def is_done(self):
        return self.cur_count >= self.aim_count

    def json(self):

        return dict(id=self.id,
                    name=self.name,
                    user_id=self.user_id,
                    type=self.type,
                    exp_value=self.exp_value,
                    aim_count=self.aim_count,
                    cur_count=self.cur_count,
                    is_done=self.is_done,
                    is_received=self.is_received,
                    date_update=format_date(self.date_update))


class ChargeCategory(db.Model):

    __tablename__  = 'charge_category'

    id = db.Column(db.Integer,primary_key=True)

    title = db.Column(db.String(500))

    cost = db.Column(db.Float,default=0.0)  #  以分为最小单位

    count = db.Column(db.Float,default=0.0)

    date_create = db.Column(db.DateTime,default=datetime.now)


    def json(self):

        return {
                'id':self.id,
                'title':self.title,
                'cost':self.cost,
                'count':self.count,
                'date_create':format_date(self.date_create)
                }


class Charge(db.Model):

    __tablename__ = 'user_charge'

    id = db.Column(UUID(),default=lambda:uuid.uuid4().hex,primary_key=True)
    charge_id = db.Column(db.String(50))
    user_id = db.Column(db.BigInteger,ForeignKey('user_info.id'))
    category_id = db.Column(db.Integer)
    order_no = db.Column(db.String(80))
    cost = db.Column(db.Float,default=0.0)  # 以分为最小单位
    count = db.Column(db.Float,default=0.0)
    success = db.Column(db.Boolean,default=False)
    date_create = db.Column(db.DateTime,default=datetime.now)


    def json(self):

        return {
                'id':self.id,
                'charge_id':self.charge_id,
                'user_id':self.user_id,
                'count':self.count,
                'cost':self.cost,
                'success':self.success,
                'date_create':format_date(self.date_create)
                }





class Gift(db.Model):

    __tablename__ = 'gift'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    introduction = db.Column(db.String(300))
    count = db.Column(db.Integer)
    pic = db.Column(db.String(300))
    local_id = db.Column(db.String(30))

    def json(self):

        return {'id':self.id,
                'name':self.name,
                'introduction':self.introduction,
                'count':self.count,
                'pic':self.pic + '?imageView/2/w/100',
                'local_id':self.local_id}


class Reward(db.Model):

    __tablename__ = 'user_reward'

    id = db.Column(db.Integer,primary_key=True)
    from_id = db.Column(db.BigInteger,db.ForeignKey(User.id),index=True)
    to_id = db.Column(db.BigInteger,db.ForeignKey(User.id),index=True)
    gift_id = db.Column(db.Integer)
    count = db.Column(db.Integer)
    date_create = db.Column(db.DateTime,default=datetime.now)



class wsbExchange(db.Model):

    """
    玩耍币账单
    """
    __tablename__ = 'wsb_exchange'

    id = db.Column(db.Integer,primary_key=True)
    wsb_count = db.Column(db.Integer)
    cny_count = db.Column(db.Float)
    user_id = db.Column(db.BigInteger,index=True)
    status = db.Column(db.String(20))
    date_create = db.Column(db.DateTime,default=datetime.now)


class cnyExchange(db.Model):

    """
    人民币账单
    """

    __tablename__ = 'cny_exchange'
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.BigInteger,index=True)
    description = db.Column(db.String(100))
    type = db.Column(db.String(20))
    cash_out_count = db.Column(db.Float) # 提现金额
    date_create = db.Column(db.DateTime,default=datetime.now)


class Report(db.Model):

    """
    用来处理举报
    """

    __tablename__ = 'report'

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.BigInteger) # 举报人
    to_user_id = db.Column(db.BigInteger) # 被举报人
    room_id = db.Column(db.Integer) #  房间 id
    content = db.Column(db.String(500))
    date_create = db.Column(db.DateTime,default=datetime.now)

