# -*- coding: utf-8 -*-
# author: notedit


import os
import sys
import time
import json
import socket
import random
import itertools
import hashlib
from hashlib import sha1, md5

from sqlalchemy import func
from sqlalchemy import desc, asc
from sqlalchemy.sql import select
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy.sql.expression import text

from park.models import backend

from park.models.models import User, Post, Group, \
    Tag, Tagmap, Reply, RecommendPos, Follow, Action, \
    Notify, Message, Channel, Version, UserAlias, VideoCache


from park.models.models import Video, Game

from park.extensions import db



def init_user():
    for idx in range(200):
        recommended = True if idx > 50 else False

        type = 'certificated' if idx > 5 and idx < 20 else 'normal'
        _d = {
            'username': u'user%03d' % idx,
            'email': 'user%02d@gmail.com' % idx,
            'avatar': 'http://tp2.sinaimg.cn/1781111701/180/5712664146/1',
            'recommended': recommended,
            'type': type,
            'id':idx
        }
        user = User(**_d)
        user.passhash('pass%02d' % idx)
        db.session.add(user)

    db.session.commit()


video_id_list = []

def init_video():
    for x in range(200):
        game = Game(name='this is a game %3d' % x,
                    package_name='com.test.game.%3d' % x,
                    game_pic='http://a4.mzstatic.com/us/r30/Purple4/v4/2f/5c/78/2f5c78ef-342f-1282-f915-891c7ebfb56c/mzl.mlywjzwj.175x175-75.jpg',
                    ios_url='https://itunes.apple.com/us/app/catchchat-chat-with-one-touch/id890404699',
                    description='this is a game description ' * 10)

        db.session.add(game)
        db.session.commit()

    video_pic = '042defa88d7711e4afe800163e000e68.png'
    video_url = '042defa88d7711e4afe800163e000e68.mp4'

    for x in range(200):

        type = 0
        is_recommended = True if x < 100 else False
        if x > 20 and x < 30:
            type = 2
        elif x > 40 and x < 50:
            type = 4
        elif x > 50 and x < 60:
            type = 5
        elif x > 60 and x < 70:
            type = 6
        elif x > 70 and x < 80:
            type = 7
        elif x > 80 and x < 90:
            type = 8
        elif x > 90:
            type = 3

        live = Video(title='this is title %3d' % (x + 1,),
                     introduction='this is introduction %3d' % x,
                     creater_id=1,
                     url=video_url,
                     encoded_url=video_url,
                     video_pic=video_pic,
                     recommended=is_recommended,
                     game_id=(x % 10) + 1,
                     type=type,
                     show=True)

        db.session.add(live)
        db.session.commit()
        video_id_list.append(live.id)

def init_video_cache():

    video_pic = '042defa88d7711e4afe800163e000e68.png'
    video_url = '042defa88d7711e4afe800163e000e68'

    live = VideoCache(title='this is title cache',
                 introduction='this is title cache',
                 creater_id=1,
                 key="042defa88d7711e4afe800163e000e68",
                 origin_url=video_url,
                 encoded_url=video_url + ".mp4",
                 video_pic=video_pic)

    db.session.add(live)
    db.session.commit()

def init_follow():
    for idx in range(100):
        for idx2 in range(20):
            follow = Follow(user_id=idx, user_id_to=idx2)
            db.session.add(follow)

        db.session.commit()


def init_channel():

    for idx in range(1,4):
        _d = {
                'channel_name':'我是一个非常赞的频道 %d' % idx,
                'pic_url':'http://7o4yvj.com1.z0.glb.clouddn.com/coverart-1406021487.jpg'
                }

        channel = Channel(**_d)
        db.session.add(channel)

    db.session.commit()

def init_version():

    for idx in range(1,10):
        _d = {
                "version_name": "0.0.%d" % idx,
                "version_log": "No log.",
                "version_url": "No url.",
                "version_type": random.randint(0,2)
            }

        version = Version(**_d)
        db.session.add(version)

    db.session.commit()

def init_group():
    for idx in range(10):
        _d = {
            'name': 'Group %02d' % idx,
            'pic_small': '/static/img/group_70x70.jpg',
            'introduction': 'introduction fafafafafa' * 10
        }
        group = Group(**_d)
        db.session.add(group)
    db.session.commit()


def init_post():
    for idx in range(500):
        _d = {
            'title': '我是一个帖子的title %03d' % idx,
            'creater_id': idx % 10 + 1,
            'content': '我是帖子内容 %03d' % idx,
            'group_id': idx % 10 + 1,
            'recommended': True if idx < 20 else False
        }
        post = Post(**_d)
        db.session.add(post)
    db.session.commit()


def init_reply():
    for idx in range(0, 100):
        _d = {
            'reply_type': 'video',
            'post_id': video_id_list[idx],
            'content': '我是评论' * 3,
            'creater_id': idx % 10 + 1
        }
        reply = Reply(**_d)
        db.session.add(reply)
    db.session.commit()

    for idx in range(100, 200):
        _index = idx - 100
        _d = {
            'reply_type': 'video',
            'post_id': video_id_list[_index],
            'content': '我是评论' * 3,
            'creater_id': idx % 10 + 1
        }
        reply = Reply(**_d)
        db.session.add(reply)
    db.session.commit()




def init_tag():
    for idx in range(1, 20):
        if idx < 10:
            tag = Tag(name='tag%02d' % idx, recommended=True)
        else:
            tag = Tag(name='tag%02d' % idx, recommended=True)

        db.session.add(tag)

    db.session.commit()

    # tagmap

    for idx in Video.query.all():
        for idx2 in range(1, 5):
            tagmap = Tagmap(tag_id=idx2, video_id=idx.id)
            db.session.add(tagmap)
    db.session.commit()


def init_recommend_pos():
    db.session.add_all([
        RecommendPos(name='index-banner-list', content=json.dumps([1, 2, 3, 4])),
        RecommendPos(name='index-video-list', content=json.dumps([1, 2, 3, 4, 5, 6, 7, 8])),
        RecommendPos(name='index-review-list', content=json.dumps([1, 2, 3, 4, 5, 6, 7, 8])),
        RecommendPos(name='index-user-list', content=json.dumps([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])),
        RecommendPos(name='index-certificated-user-list', content=json.dumps([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])),
        RecommendPos(name='index-strategy-list', content=json.dumps([1, 2, 3, 4, 5, 6, 7, 8]))])

    db.session.commit()


def init_follow_action():
    # 'daily_review','new_review','new_short_review'
    action1 = Action(user_id=3, action_type='daily_review', content_id=2,
                     attach_id=2)
    action2 = Action(user_id=3, action_type='new_review', content_id=3,
                     attach_id=2)
    action3 = Action(user_id=3, action_type='new_short_review', content_id=4,
                     attach_id=2)

    db.session.add(action1)
    db.session.add(action2)
    db.session.add(action3)
    db.session.commit()


    # new_note

    action4 = Action(user_id=3, action_type='new_note', content_id=5,
                     attach_id=2)

    db.session.add(action4)
    db.session.commit()


    # 'new_film','share_film','buy_film','like_film'

    action5 = Action(user_id=3, action_type='new_film', content_id=5)
    action6 = Action(user_id=3, action_type='share_film', content_id=6)
    action7 = Action(user_id=3, action_type='buy_film', content_id=6)
    action8 = Action(user_id=3, action_type='like_film', content_id=6)
    db.session.add_all([action5, action8, action6, action7])
    db.session.commit()

    # new_post

    action9 = Action(user_id=3, action_type='new_post', content_id=6)
    db.session.add(action9)
    db.session.commit()



def init_user_notify():

    # 关注
    backend.push_notify(3, 'follow_user', 4)
    backend.push_notify(3, 'follow_user', 6)
    backend.push_notify(3, 'follow_user', 8)

    # 'reply_video'

    backend.push_notify(3, 'reply_video', 4, content_id=video_id_list[0],reply_id=1)
    backend.push_notify(3, 'reply_video', 4, content_id=video_id_list[0],reply_id=2)


    # 'reply_reply',


    backend.push_notify(3, 'reply_reply', 6, content_id=video_id_list[0],reply_id=5)
    backend.push_notify(3, 'reply_reply', 6, content_id=video_id_list[0],reply_id=6)



    # 'like_video'

    backend.push_notify(3, 'like_video', 8, content_id=video_id_list[1])

    backend.push_notify(3, 'like_video', 8, content_id=video_id_list[3])



#固定一个 token  供 android 客户端测试用
def init_user03():
    user = User.query.get_or_404(3)

    user.token = 'c2ad2eae8d7611e4a25200163e000e68'

    db.session.commit()

#生产环境，数据初始化

def init_true_user():
    
    user_lianxiang_weibo = {
            'username': u'刘连响',
            'email': 'lianxiang@wan123.tv',
            'recommended': True,
            'type': "certificated",
            'id': '894907519741199578',
            'avatar': 'http://tp2.sinaimg.cn/1781111701/180/5712664146/1'
        }

    user_alias_lianxiang_weibo = {
            'user_id': '894907519741199578',
            'open_id': '1781111701',
            'access_token': '2.00FW3XwBx5aT2C13cf3b95f66lrtUB',
            'type': 'weibo'
    }

    db.session.add(User(**user_lianxiang_weibo))
    db.session.add(UserAlias(**user_alias_lianxiang_weibo))

    user_lianxiang_qq = {
            'username': u'刘连响890',
            'email': 'lianxiang_@wan123.tv',
            'recommended': True,
            'type': "certificated",
            'id': '896742976615613664',
            'avatar': 'http://qzapp.qlogo.cn/qzapp/1103881743/196AC3B5DF7BDF19724130BE94FE9AA4/100'
        }

    user_alias_lianxiang_qq = {
            'user_id': '896742976615613664',
            'open_id': '196AC3B5DF7BDF19724130BE94FE9AA4',
            'access_token': '8D03B2945CB7CCEA8B00B0047915C7CF',
            'type': 'qq'
    }

    db.session.add(User(**user_lianxiang_qq))
    db.session.add(UserAlias(**user_alias_lianxiang_qq))

    user_dexin_qq = {
            'username': u'DOVE',
            'email': 'dexin@wan123.tv',
            'recommended': True,
            'type': "certificated",
            'id': '896846066895291623',
            'avatar': 'http://qzapp.qlogo.cn/qzapp/1103881743/8EF2158056109A5FA21F63CD50BD799F/100'
        }

    user_alias_dexin_qq = {
            'user_id': '896846066895291623',
            'open_id': '8EF2158056109A5FA21F63CD50BD799F',
            'access_token': '2DB55E7EB868EDE5A86703ED09AB7E08',
            'type': 'qq'
    }

    db.session.add(User(**user_dexin_qq))
    db.session.add(UserAlias(**user_alias_dexin_qq))

    user_liudian_qq = {
            'username': u'艰苦啊.avi',
            'email': 'liudian@wan123.tv',
            'recommended': True,
            'type': "certificated",
            'id': '896757236410352868',
            'avatar': 'http://qzapp.qlogo.cn/qzapp/1103881743/F37B53F2D58C38F04A9B4E9F9BF5C7D4/100'
        }

    user_alias_liudian_qq = {
            'user_id': '896757236410352868',
            'open_id': 'F37B53F2D58C38F04A9B4E9F9BF5C7D4',
            'access_token': '72F61DCF51B28C49009D0AADEB858D15',
            'type': 'qq'
    }

    db.session.add(User(**user_liudian_qq))
    db.session.add(UserAlias(**user_alias_liudian_qq))

    user_ones_qq = {
            'username': u'千水丶阳',
            'email': 'ones@wan123.tv',
            'recommended': True,
            'type': "certificated",
            'id': '896748029233595617',
            'avatar': 'http://qzapp.qlogo.cn/qzapp/1103881743/EDCEB00CCDD56CB38A9183165DF38DF4/100'
        }

    user_alias_ones_qq = {
            'user_id': '896748029233595617',
            'open_id': 'EDCEB00CCDD56CB38A9183165DF38DF4',
            'access_token': '3924DD04BBEE9A0F2E6C3384E1496D1D',
            'type': 'qq'
    }

    db.session.add(User(**user_ones_qq))
    db.session.add(UserAlias(**user_alias_ones_qq))

    db.session.commit()

def init_true_video():
    pass

def init_all():

    if socket.gethostname().startswith('aliyun'):
        init_true_user()
        init_true_video()
    else:
        init_user()
        init_true_user()
        # init_follow()
        # init_video()
        # init_video_cache()
        # init_group()
        # init_post()
        # init_reply()
        # init_tag()
        # init_recommend_pos()
        # init_follow_action()
        # init_user_notify()
        # init_channel()
        # init_version()
        #
        # init_user03()
