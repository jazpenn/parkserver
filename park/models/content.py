# -*- coding: utf-8 -*-
# author: leeoxiang

import types
import time
import random
import hashlib
import contextlib
from datetime import date
from datetime import datetime
from datetime import timedelta
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy import Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm import create_session
from sqlalchemy.orm import aliased
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, Text, Boolean, Sequence, Integer, \
    String, PickleType, MetaData, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM, ARRAY, Any, All
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy import desc, asc
from sqlalchemy import func
from sqlalchemy import distinct
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.sqlalchemy import BaseQuery
from flask import current_app
from park.extensions import db, influx_client, redis_rank
from park.cacheutil import func_redis_cache
from park.helpers import BackendError, register, assert_error
from park import signals
from .models import RecommendPos, User, Group, Follow,Danmu,Reply, Post, WatchHistory, Tag, Tagmap, Like, Rating, Vote, Storage
from .models import Video, Game, Channel, Danmu, UserTask,Collect,Reward,Live,Charge


# ####################### 新的后端  ###########################################
@register('get_recommend_video_list')
def get_recommend_video_list(offset=0, limit=18):
    videos = Video.query.filter(Video.recommended == True). \
        order_by(Video.id.desc()).limit(limit).offset(offset).all()

    return videos


@register('get_index_recommend_list')
def get_index_recommend_list():
    _list = RecommendPos.query.get_value('index-recommend-list')
    if _list is None:
        raise BackendError('RecommendlistError', 'does not exist')
    if not _list: return []
    videos = Video.query.filter(Video.id.in_(_list))
    return videos


# 按照一周之内的观看次数
@register('get_popular_video_list')
def get_popular_video_list(offset=0, limit=18):
    date_limit = datetime.now() + timedelta(days=-7)
    res = db.session.query(View.video_id, func.count(View.id).label('total')). \
        filter(View.date_create > date_limit). \
        group_by(View.video_id).order_by('total desc').offset(offset).limit(limit).all()

    if not res: return []
    _ids = [r[0] for r in res]
    popular_videos = Video.query.filter(Video.id.in_(_ids)).all()
    return popular_videos


@register('get_hot_video_list')
def get_hot_video_list(offset=0, limit=18):
    hot_videos = Video.query.filter(Video.show == True). \
        order_by(Video.play_count.desc()).limit(limit).offset(offset).all()

    return hot_videos



@register('get_video_count')
def get_video_count():
    count = Video.query.filter(Video.show == True).count()

    return count


# @register('get_user_like_video')
# def get_user_like_video(user_id, limit=6, offset=0):

#     videos = Video.query.join(Like, and_(Video.id==Like.content_id, Like.content_type=='video')). \
#         filter(Like.user_id==user_id, Video.show==True). \
#         order_by(Like.date_create.desc()). \
#         limit(limit).offset(offset).all()

#     return videos

@register('get_relate_video')
def get_relate_video(video_id, game_id, count=5):
    if not game_id:
        return []

    videos = Video.query.filter(Video.game_id == game_id).filter(Video.id != video_id). \
        limit(count).all()

    return videos


# 得到游戏的popular 视频
@register('get_game_popular_video')
def get_game_popular_video(game_id,offset=0,limit=10):
    # todo 先写一个假的

    videos = Video.query.filter(Video.game_id == game_id).\
            order_by(Video.play_count.desc()).limit(limit).\
            offset(offset).all()

    return videos


# 单个游戏最新的视频
@register('get_game_latest_video')
def get_game_latest_video(game_id, offset=0, limit=10):
    videos = Video.query.filter(Video.game_id == game_id).order_by(Video.date_create.desc()). \
        offset(offset).limit(limit).all()

    return videos


# 获得全部的游戏玩家
@register('get_user_list')
def get_user_list(recommended=None, limit=20, offset=0):
    if recommended:
        users = User.query.filter(User.recommended == True).limit(limit).offset(offset).all()
    else:
        users = User.query.limit(limit).offset(offset).all()

    return users

@register('get_user_count')
def get_user_count(recommended=None):
    if recommended:
        count = User.query.filter(User.recommended == True).count()
    else:
        count = User.query.count()

    return count

# 获取推荐主播
@register('get_recommended_user_list')
def get_recommended_user_list(limit=20, offset=0, random=False):

    users = User.query.filter(User.recommended==True)

    if random:
        users = users.order_by(func.random())

    return users.limit(limit).offset(offset).all()

# 按最新推荐视频获取推荐主播
@register('get_user_by_latest_video')
def get_user_by_latest_video(limit=20, offset=0):

    users = db.session.query(User, func.sum(Video.play_count).label("all_play_count"),\
        func.max(Video.date_create).label('latest_video_date_create')).\
        join(Video).filter(User.type=='certificated').group_by(User).\
        order_by("latest_video_date_create desc").limit(limit).offset(offset).all()

    return users

# 按播放量获取推荐主播
@register('get_user_by_play_count')
@func_redis_cache(300)
def get_user_by_play_count(limit=20, offset=0):

    users = db.session.query(User, func.sum(Video.play_count).label("all_play_count")).\
        join(Video).group_by(User).order_by("all_play_count desc").\
        limit(limit).offset(offset).all()

    return users

# 获取推荐主播和视频数
@register('get_user_and_video_count')
def get_user_and_video_count(limit=20, offset=0, recommended=None):

    users = db.session.query(User, func.count(Video.id).label("video_count")).\
        join(Video).filter(Video.show==True).group_by(User).order_by('video_count desc')

    if recommended:
        users = users.filter(User.recommended==True)

    users = users.limit(limit).offset(offset).all()

    return users

# 获取当月主播排行及热度
@register('get_user_hot_rank')
def get_user_hot_rank(limit=20, offset=0):

    start = offset
    stop = offset + limit - 1

    re = redis_rank.UserHotRank.get_rank(start, stop, 7)

    print(re)

    if not re:
        return []

    re = dict(re)

    users = User.query.filter(User.id.in_(re.keys())).all()
    _users = []
    for each_user in users:
        each_user.__setattr__('rank_value', re[str(each_user.id)])
        _users.append(each_user)

    return sorted(_users, key=lambda x: x.rank_value, reverse=True)


@register('get_user_by_follower')
def get_user_by_follower(offset=0,limit=20):

    users = User.query.order_by(User.follower_count.desc()).\
            offset(offset).limit(limit).all()

    return users



@register('get_latest_video')
def get_latest_video(limit=20, offset=0, recommended=None):

    videos = Video.query.filter(Video.show==True).order_by('date_create desc')

    if recommended:
        videos = videos.filter(Video.recommended==True)

    videos = videos.limit(limit).offset(offset).all()

    return videos

@register('get_latest_user_latest_video')
def get_latest_user_latest_video(limit=20, offset=0):

    users = db.session.query(User, func.min(Video.date_create).label('min_video_create_date')).\
        join(Video, and_(Video.creater_id==User.id, Video.show==True)).group_by(User).\
        order_by('min_video_create_date desc')

    users = users.limit(limit).offset(offset).all()
    users = [each[0] for each in users]

    videos = []
    for each_user in users:
        first_video = Video.query.filter(Video.creater_id==each_user.id).\
            order_by('date_create').first()
        videos.append(first_video)

    return videos

@register('get_user_with_video_count')
def get_user_with_video_count():

    count = User.query.join(Video).distinct().count()

    return count

@register('get_latest_video_count')
def get_latest_video_count(limit=20, offset=0, recommended=None):

    videos = Video.query.filter(Video.show==True).order_by('date_create desc')

    if recommended:
        videos = videos.filter(Video.recommended==True)

    count = videos.count()

    return count


# BEE_USER_IDS = [
#             987495330050213548L, 966483537366615440L, 987495330108933813L,
#             987495330092156594L, 987495330117322422L, 987495329781778087L,
#             987495330125711031L, 987495330134099641L, 966982673534813645L,
#             977542613408155397L, 987495329689503398L, 987495330083767985L,
#             967243393124009497L, 966603053723551150L, 987495330100545203L,
#             987495330025047722L, 987495330075379376L, 967258626567702046L,
#             987495330066990766L, 987495330134099640L, 968463855543912191L,
#             987495330058602157L, 967818116874634869L, 987495330108933812L,
#             977542613903083272L, 987495330066990767L, 987495330033436331L,
#             941990410715137509L, 977542613735311110L, 977542613819197191L,
#             987495329857275560L, 987495329941161641L, 977544414761060105L
#             ]

@register('get_active_user')
@func_redis_cache(300)
def get_active_user(limit=12, offset=0, days=1):

    # date_limit = datetime.now() + timedelta(days=-30)

    # users = db.session.query(User, func.count(Reply.id).label('reply_count')).\
    #     filter(User.id.notin_(BEE_USER_IDS)).\
    #     join(Reply, and_(Reply.creater_id==User.id, Reply.date_create>=date_limit)).\
    #     order_by('reply_count desc').group_by(User)

    # users = users.limit(limit).offset(offset).all()

    start = offset
    stop = offset + limit - 1

    re = redis_rank.UserActivityRank.get_rank(start, stop, days)

    if not re:
        return []

    re = dict(re)

    users = User.query.filter(User.id.in_(re.keys())).all()
    _users = []
    for each_user in users:
        each_user.__setattr__('active_value', re[str(each_user.id)])
        _users.append(each_user)

    return sorted(_users, key=lambda x: x.active_value, reverse=True)

@register('get_active_user_count')
def get_active_user_count(days=1):

    # date_limit = datetime.now() + timedelta(days=-30)

    # count = User.query.join(Reply,\
    #         and_(Reply.creater_id==User.id, Reply.date_create>=date_limit)).count()

    # return count

    re = redis_rank.UserActivityRank.get_rank(0, -1, days)

    return len(re)

# 游戏相关

# 热门游戏
@register('get_hot_game')
def get_hot_game(limit=20, offset=0):
    # todo 先有数据再优化
    games = Game.query.filter(Game.game_pic!=None).order_by(Game.id.desc()).limit(limit).offset(offset).all()

    return games


@register('get_game_video_count')
def get_game_video_count(game_id):

    return Video.query.filter(Video.game_id==game_id).filter(Video.show == True).count()


# iOS游戏
@register('get_game_list')
def get_game_list(type, limit=20, offset=0):
    if type == 'ios':
        games = Game.query.filter(Game.type.in_([2, 3])).order_by(Game.date_create.desc()). \
            limit(limit).offset(offset).all()

    elif type == 'android':
        games = Game.query.filter(Game.type.in_([1, 3])).order_by(Game.date_create.desc()). \
            limit(limit).offset(offset).all()
    else:

        games = Game.query.order_by(Game.date_create.desc()). \
            limit(limit).offset(offset).all()

    return games


@register('get_game_count')
def get_game_count(type):
    if type == 'ios':
        count = Game.query.filter(Game.type.in_([2, 3])).count()
    elif type == 'android':
        count = Game.query.filter(Game.type.in_([1, 3])).count()
    else:
        count = Game.query.count()

    return count


@register('get_user_watch_list')
def get_user_watch_list(user_id, limit=4, offset=0):
    _watchs = WatchHistory.query.filter(WatchHistory.user_id == user_id).\
            filter(WatchHistory.deleted == False).limit(limit).offset(offset).all()

    if len(_watchs) == 0: return []


    return _watchs


@register('get_user_watch_count')
def get_user_watch_count(user_id):
    return WatchHistory.query.filter(WatchHistory.user_id == user_id).filter(WatchHistory.deleted == False).count()


@register('get_user_video_list')
def get_user_video_list(user_id, limit=4, offset=0):
    videos = Video.query.filter(Video.show == True).filter(Video.creater_id == user_id). \
        order_by(Video.date_create.desc()).limit(limit).offset(offset).all()

    return videos


@register('get_user_video_count')
def get_user_video_count(user_id):
    count = Video.query.filter(Video.show == True).filter(Video.creater_id == user_id).count()

    return count


@register('get_user_live_list')
def get_user_live_list(user_id, limit=4, offset=0,with_live=False):
    lives = Live.query.filter(Live.show == True).filter(Live.user_id == user_id)

    if with_live:
        lives = lives.filter(Live.status =='connected')
    else:
        lives = lives.filter(Live.status != 'connected')

    lives = lives.order_by(Live.date_create.desc()).limit(limit).offset(offset).all()

    return lives


@register('get_user_live_count')
def get_user_live_count(user_id,with_live=False):

    if with_live:
        count = Live.query.filter(Live.show == True).filter(Live.user_id == user_id).\
                filter(Live.status == 'connected').count()
    else:
        count = Live.query.filter(Live.show == True).filter(Live.user_id == user_id).\
                    filter(Live.status != 'connected').count()

    return count





@register('vote_video')
def vote_video(user_id, video_id):
    vote = Vote(user_id=user_id, video_id=video_id, type='up')
    try:
        db.session.add(vote)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        vote = None

    if vote is None:
        vote = Vote.query.filter(and_(Vote.user_id == user_id, Vote.video_id == video_id)).first()
        vote.type = 'up'
        db.session.commit()

    return vote


@register('unvote_video')
def unvote_video(user_id, video_id):
    vote = Vote.query.filter(and_(Vote.user_id == user_id, Vote.video_id == video_id)).first()
    if vote:
        vote.type = 'down'
        db.session.commit()

    else:
        vote = Vote(user_id=user_id, video_id=video_id, type='down')
        try:
            db.session.add(vote)
            db.session.commit()
        except:
            db.session.rollback()


########################  新的后端结束  ########################################


@register('get_banner_list')
def get_banner_list(limit=4):
    videos = Video.query.filter(Video.is_banner == True).filter(Video.show == True). \
        order_by(Video.date_create.desc()).limit(limit).all()

    return videos

@register('get_recommend_list')
def get_recommend_list(limit=20, offset=0, random=False, days=None):

    videos = Video.query.filter(and_(Video.show == True, Video.recommended == True))

    if days:
        date_limit = datetime.now() + timedelta(days=-days)
        videos = Video.query.filter(Video.date_create > date_limit)

    if random:
        videos = videos.order_by(func.random())
    else:
        videos = videos.order_by(Video.date_create.desc())

    videos = videos.limit(limit).offset(offset).all()

    return videos



# 推荐主播
@register('get_user_recommend_list')
def get_user_recommend_list(limit=20,offset=0):

    users = User.query.filter(User.recommended == True).\
                limit(limit).offset(offset).all()

    return users

# 推荐主播的数量
@register('get_user_recommend_count')
def get_user_recommend_count():

    return User.query.filter(User.recommended == True).count()


# 直播回放推荐列表
@register('get_replay_recommend_list')
def get_replay_recommend_list(limit=20, offset=0, random=False, days=None):

    lives = Live.query.filter(Live.recommended == True)

    if days:
        date_limit = datetime.now() + timedelta(days=-days)
        lives = Live.query.filter(Live.date_create > date_limit)

    if random:
        lives = lives.order_by(func.random())
    else:
        lives = lives.order_by(Live.date_create.desc())

    lives = lives.limit(limit).offset(offset).all()

    return lives


# 直播回放推荐列表数量
@register('get_replay_recommend_count')
def get_replay_recommend_count():

    return Live.query.filter(Live.recommended == True).count()




@register('get_recommend_list_by_index')
def get_recommend_list_by_index(position, limit=20, offset=0):

    video_ids = RecommendPos.query.get_value(position)
    videos = Video.query.filter(Video.id.in_(video_ids)) if video_ids else []

    videos = videos.order_by(Video.id.desc()).limit(limit).offset(0).all() if videos else []

    return videos

@register('get_recommend_count')
def get_recommend_count(days=None):

    videos = Video.query.filter(and_(Video.recommended == True, Video.show == True))

    if days:
        date_limit = datetime.now() + timedelta(days=-days)
        videos = Video.query.filter(Video.date_create > date_limit)

    count = videos.count()

    return count


@register('get_hot_list')
def get_hot_list(limit=20, offset=0, days=7):

    # videos = Video.query.filter(Video.show == True)

    # if days:
    #     date_limit = datetime.now() + timedelta(days=-days)
    #     videos = videos.filter(Video.date_create > date_limit)

    # videos = videos.order_by(Video.play_count.desc()).limit(limit).offset(offset).all()

    # return videos

    start = offset
    stop = offset + limit - 1

    re = redis_rank.VideoHotRank.get_rank(start, stop, days)

    if not re:
        return []

    re = dict(re)

    videos = Video.query.filter(Video.id.in_(re.keys())).all()
    _videos = []
    for each_video in videos:
        each_video.__setattr__('rank_value', re[str(each_video.id)])
        _videos.append(each_video)

    return sorted(_videos, key=lambda x: x.rank_value, reverse=True)

@register('get_hot_list_count')
def get_hot_list_count(days=1):

    # videos = Video.query.filter(Video.show == True)

    # if days:
    #     date_limit = datetime.now() + timedelta(days=-days)
    #     videos = videos.filter(Video.date_create > date_limit)

    # count = videos.count()

    # return count

    re = redis_rank.VideoHotRank.get_rank(0, -1, days)

    return len(re)

@register('get_latest_list')
def get_latest_list(limit=20, offset=0):
    videos = Video.query.filter(and_(Video.show == True, Video.encoded_url != None)).order_by(Video.date_create.desc()). \
        limit(limit).offset(offset).all()

    return videos

@register('get_latest_reply')
def get_latest_reply(limit=20, offset=0):
    replys = Reply.query.filter(Reply.reply_type=="video").join(Video, Video.id==Reply.post_id).filter(Video.show==True).order_by(Reply.date_create.desc()). \
        limit(limit).offset(offset).all()

    return replys

@register('get_index_banner_list')
def get_index_banner_list():
    _list = RecommendPos.query.get_value('index-banner-list')
    if _list is None:
        raise BackendError('BannerlistError', 'does not exist')
    if not _list: return []
    videos = Video.query.filter(Video.id.in_(_list)).all()
    return videos


@register('get_index_video_list')
def get_index_video_list():
    _list = RecommendPos.query.get_value('index-video-list')
    if _list is None:
        raise BackendError('VideoListError', 'does not exist')
    if not _list: return []
    videos = Video.query.filter(Video.id.in_(_list)).all()
    return videos


@register('get_index_review_list')
def get_index_review_list():
    _list = RecommendPos.query.get_value('index-review-list')
    if _list is None:
        raise BackendError('ReviewListError', 'does not exist')
    if not _list: return []
    videos = Video.query.filter(Video.id.in_(_list)).all()
    return videos


@register('get_index_strategy_list')
def get_index_strategy_list():
    _list = RecommendPos.query.get_value('index-strategy-list')
    if _list is None:
        raise BackendError('StrategyListError', 'does not exist')
    if not _list: return []
    videos = Video.query.filter(Video.id.in_(_list)).all()
    return videos


@register('get_index_film_list')
def get_index_film_list():
    _list = RecommendPos.query.get_value('index-film-list')
    if _list is None:
        raise BackendError('FilmlistError', 'does not exist')
    if not _list: return []
    films = Film.query.filter(Film.id.in_(_list))
    return films


@register('get_index_channel')
def get_index_channel(limit=6):
    _list = Channel.query.filter(and_(Channel.show==True,\
        Channel.is_banner==True)).order_by(Channel.order.desc()).limit(limit).all()
    return _list



@register('get_all_group')
def get_all_group():
    groups = Group.query.order_by(Group.date_create.desc()).all()
    return groups


# 三天之内回复的个数
@register('get_hot_post')
def get_host_post():
    date_limit = datetime.now() + timedelta(days=-3)
    res = db.session.query(Reply.post_id, func.count(Reply.id).label('total')). \
        filter(Reply.group_id != -1).filter(Reply.date_create > date_limit). \
        group_by(Reply.post_id).order_by('total desc').limit(5).all()

    if not res: return []
    hot_post_ids = [r[0] for r in res]
    hot_posts = Post.query.filter(Post.id.in_(hot_post_ids)).all()
    return hot_posts


@register('get_group_active_user')
def get_group_active_user(group_id, limit=8):
    res = db.session.query(Reply.creater_id, func.count(Reply.id).label('total')). \
        filter(Reply.group_id == group_id). \
        group_by(Reply.creater_id).order_by('total desc').limit(limit).all()

    if not res: return []
    user_ids = [r[0] for r in res]
    users = User.query.filter(User.id.in_(user_ids)).all()
    return users


# 精选 电影
@register('get_film_recommend_list')
def get_film_recommend_list(limit=10, offset=0, cost=False):
    if cost:
        films = Film.query.filter(and_(Film.recommended == True, Film.price >= 0, Film.show == True)). \
            order_by(Film.date_update.desc()).limit(limit).offset(offset).all()
    else:
        films = Film.query.filter(and_(Film.recommended == True, Film.price == -1, Film.show == True)). \
            order_by(Film.date_update.desc()).limit(limit).offset(offset).all()

    return films


# 全部电影  新片
@register('get_film_list')
def get_film_list(limit=10, offset=0):
    films = Film.query.filter(Film.show == True).order_by(Film.date_create.desc()).limit(limit). \
        offset(offset).all()

    return films


# 全部电影  数量
@register('get_film_count')
def get_film_count():
    return Film.query.filter(Film.show == True).count()


# 购买最多的列表
@register('get_top_buy_list')
def get_top_buy_list(limit=10, offset=0):
    _films_ids = db.session.query(Buy.film_id, func.count(Buy.id).label('total')). \
        group_by(Buy.film_id).order_by('total desc'). \
        limit(limit).offset(offset).all()
    film_ids = [f[0] for f in _films_ids]

    if len(film_ids) == 0: return []

    films = Film.query.filter(Film.show == True).filter(Film.id.in_(film_ids)).all()
    return films


# 获取所有被人买过的电影 的数量
@register('get_top_buy_count')
def get_top_buy_count():
    count = db.session.query(Buy.film_id).group_by(Buy.film_id).count()
    return count


# 已购商品
@register('get_user_buyed_list')
def get_buyed_list(user_id, limit=10, offset=0):
    buys = Buy.query.filter_by(user_id=user_id).order_by(Buy.date_create). \
        limit(limit).offset(offset).all()

    film_ids = [b.film_id for b in buys]

    if len(film_ids) == 0: return []

    films = Film.query.filter(Film.show == True).filter(Film.id.in_(film_ids)).all()
    return films


# 已购商品的log
@register('get_user_buy_log')
def get_user_buy_log(user_id, limit=10, offset=0):
    buys = Buy.query.filter_by(user_id=user_id).order_by(Buy.date_create). \
        limit(limit).offset(offset).all()
    return buys


# 用户购买的数量
@register('get_user_buyed_count')
def get_user_buyed_count(user_id):
    count = Buy.query.filter_by(user_id=user_id).count()
    return count


# 充值记录
@register('get_user_charge_list')
def get_user_charge_list(user_id, offset=0, limit=10):
    charges = Charge.query.filter(and_(Charge.user_id == user_id, Charge.success == True)).order_by(Charge.date_create). \
        limit(limit).offset(offset).all()

    return charges


@register('get_user_charge_count')
def get_user_charge_count(user_id):
    count = Charge.query.filter(and_(Charge.user_id == user_id, Charge.success == True)).count()
    return count


# 受欢迎的影评  其实是推荐的  等后面内容多了之后增加推荐算法
@register('get_recommend_review_list')
def get_recommend_review_list(offset=0, limit=10):
    reviews = Review.query.filter(and_(Review.recommended == True, Review.type == 'review', Review.show == True)). \
        order_by(Review.date_update.desc()).limit(limit).offset(offset).all()
    return reviews


@register('get_recommend_review_count')
def get_recommend_review_count():
    count = Review.query.filter(and_(Review.recommended == True, Review.type == 'review', Review.show == True)).count()
    return count


@register('get_recommend_short_review_list')
def get_recommend_short_review_list(offset=0, limit=10):
    reviews = Review.query.filter(and_(Review.recommended == True, Review.type == 'short_review', Review.show == True)). \
        order_by(Review.date_update.desc()).limit(limit).offset(offset).all()

    return reviews


@register('get_recommend_short_review_count')
def get_recommend_short_review_count():
    count = Review.query.filter(
        and_(Review.recommended == True, Review.type == 'short_review', Review.show == True)).count()
    return count


# 影评人列表
@register('get_review_user_list')
def get_review_user_list(offset=0, limit=10):
    # 先查到有发影评的人

    user_res = db.session.query(Review.creater_id, func.max(Review.date_create).label('date_create')).filter(
        Review.type == 'review') \
        .group_by(Review.creater_id).order_by('date_create desc').limit(limit).offset(offset).all()

    user_ids = [u[0] for u in user_res]

    if not user_ids: return []

    users = User.query.filter(User.id.in_(user_ids)).all()

    return users


@register('get_review_user_count')
def get_review_user_count():
    # count = db.session.query(func.count(distinct(Review.creater_id))).scalar()
    count = db.session.query(Review.creater_id, func.max(Review.date_create).label('date_create')).filter(
        Review.type == 'review') \
        .group_by(Review.creater_id).order_by('date_create desc').count()

    return count


# 一个电影的影评 影评
@register('get_film_review_list')
def get_film_review_list(film_id, limit=10, offset=0):
    reviews = Review.query.filter(and_(Review.film_id == film_id, Review.type == 'review', Review.show == True)). \
        order_by(Review.date_create.desc()).limit(limit).offset(offset).all()
    return reviews


# 一个电影影评的个数
@register('get_film_review_count')
def get_film_review_count(film_id):
    count = Review.query.filter(and_(Review.film_id == film_id, Review.type == 'review', Review.show == True)).count()
    return count


# 一个电影的  短评
@register('get_film_short_review_list')
def get_film_short_review_list(film_id, limit=10, offset=0):
    reviews = Review.query.filter(and_(Review.film_id == film_id, Review.type == 'short_review', Review.show == True)). \
        order_by(Review.date_create.desc()).limit(limit).offset(offset).all()
    return reviews


# 一个电影短评的个数
@register('get_film_short_review_count')
def get_film_short_review_count(film_id):
    count = Review.query.filter(
        and_(Review.film_id == film_id, Review.type == 'short_review', Review.show == True)).count()
    return count


@register('get_film_note_list')
def get_film_note_list(film_id, limit=10, offset=0):
    notes = Note.query.filter(and_(Note.film_id == film_id, Note.show == True)).order_by(Note.date_create.desc()). \
        limit(limit).offset(offset).all()

    return notes


@register('get_film_note_count')
def get_film_note_count(film_id):
    count = Note.query.filter(and_(Note.film_id == film_id, Note.show == True)).count()
    return count


# 获得一个对象的评论列表
@register('get_object_reply_list')
def get_object_reply_list(oid, otype, limit=10, offset=0, reverse=False):
    replys = Reply.query.filter(and_(Reply.post_id == oid, Reply.reply_type == otype))

    if reverse:
        replys = replys.order_by(Reply.date_create.desc())
    else:
        replys = replys.order_by(Reply.date_create.asc())

    replys = replys.limit(limit).offset(offset).all()

    return replys

@register('get_object_reply_list_desc')
def get_object_reply_list_desc(oid, otype, limit=10, offset=0):
    replys = Reply.query.filter(and_(Reply.post_id == oid, Reply.reply_type == otype)). \
        order_by(Reply.date_create.desc()).limit(limit).offset(offset).all()
    return replys

# 获得一个对象的评论个数
@register('get_object_reply_count')
def get_object_reply_count(oid, otype):
    count = Reply.query.filter(and_(Reply.post_id == oid, Reply.reply_type == otype)).count()
    return count

# 获得所有的弹幕

@register('get_object_danmu_list')
def get_object_danmu_list(oid,otype):
    replys = Danmu.query.filter(and_(Danmu.post_id == oid, Danmu.reply_type == otype)). \
        order_by(Danmu.date_create.asc()).all()
    return replys





# 获得受欢迎的手记
@register('get_recommend_note_list')
def get_recommend_note_list(offset=0, limit=10):
    notes = Note.query.filter(and_(Note.recommended == True, Note.show == True)).order_by(Note.date_update.desc()). \
        limit(limit).offset(offset).all()

    return notes


@register('get_recommend_note_count')
def get_recommend_note_count():
    count = Note.query.filter(and_(Note.recommended == True, Note.show == True)).count()
    return count


# 创作人 列表
@register('get_note_user_list')
def get_note_user_list(offset=0, limit=10):
    # 先查到有发影评的人

    user_res = db.session.query(Note.creater_id, func.max(Note.date_create).label('date_create')).group_by(
        Note.creater_id). \
        order_by('date_create desc').limit(limit).offset(offset).all()

    user_ids = [u[0] for u in user_res]

    if not user_ids: return []

    users = User.query.filter(User.id.in_(user_ids))

    return users


# 小组话题列表
@register('get_post_list')
def get_post_list(limit=20, offset=0):
    posts = Post.query.filter(Post.show == True).order_by(Post.date_update.desc()).limit(limit).offset(offset).all()
    return posts


@register('get_post_count')
def get_post_count():
    count = Post.query.filter_by(show=True).count()
    return count


@register('get_user_post_list')
def get_user_post_list(user_id, limit=20, offset=0):
    posts = Post.query.filter(and_(Post.creater_id == user_id, Post.show == True)). \
        order_by(Post.date_update.desc()).limit(limit).offset(offset).all()

    return posts


@register('get_user_post_count')
def get_user_post_count(user_id):
    count = Post.query.filter(and_(Post.creater_id == user_id, Post.show == True)).count()
    return count


# 用户 回复过的帖子
@register('get_user_reply_post_list')
def get_user_reply_post_list(user_id, limit=20, offset=0):
    _posts_ids = db.session.query(Reply.post_id).filter(and_(Reply.reply_type == 'post', Reply.creater_id == user_id)). \
        group_by(Reply.post_id).all()

    post_ids = [p[0] for p in _posts_ids]

    if len(post_ids) == 0: return []

    posts = Post.query.filter(Post.id.in_(post_ids)).filter(Post.show == True).order_by(Post.date_update.desc()). \
        limit(limit).offset(offset).all()

    return posts


@register('get_user_reply_post_count')
def get_user_reply_post_count(user_id):
    count = db.session.query(Reply.post_id).filter(and_(Reply.reply_type == 'post', Reply.creater_id == user_id)). \
        group_by(Reply.post_id).count()

    return count


# 获取一个小组最新的话题
@register('get_group_post_list')
def get_group_post_list(group_id, limit=20, offset=0):
    posts = Post.query.filter_by(group_id=group_id).filter(Post.show == True).order_by(Post.date_create.desc()). \
        limit(limit).offset(offset).all()
    return posts


# 获取小组里面 最后更新的话题
@register('get_group_latest_update_post_list')
def get_group_latest_update_post_list(group_id, limit=10, offset=0):
    posts = Post.query.filter_by(group_id=group_id).filter(Post.show == True).order_by(Post.date_update.desc()). \
        limit(limit).offset(offset).all()
    return posts


# 获取一个小组 话题的数量
@register('get_group_post_count')
def get_group_post_count(group_id):
    count = Post.query.filter_by(group_id=group_id).filter(Post.show == True).count()
    return count


# 发现话题   现在的逻辑是 推荐的话题 按照最后回复时间排序
@register('get_recommend_post_list')
def get_recommend_post_list(limit=20, offset=0):
    posts = Post.query.filter(Post.recommended == True).filter(Post.show == True).order_by(Post.date_update.desc()). \
        limit(limit).offset(offset).all()

    return posts


# 同上  获得数量
@register('get_recommend_post_count')
def get_recommend_post_count():
    count = Post.query.filter(Post.recommended == True).filter(Post.show == True).count()
    return count


###########  观看相关  观看过的记录 ##############
@register('watch_video')
def watch_video(user_id, video_id,stop_time=0):
    watch = WatchHistory(user_id=user_id, video_id=video_id,stop_time=stop_time)
    try:
        db.session.add(watch)
        db.session.commit()
    except:
        db.session.rollback()


@register('delete_one_watch')
def delete_one_watch(watch_id):

    WatchHistory.query.filter_by(id=watch_id).update({'deleted':True})

    db.session.commit()


@register('delete_user_watch')
def delete_user_watch(user_id):

    WatchHistory.query.filter_by(user_id=user_id).update({'deleted':True})

    db.session.commit()


########## 是否喜欢  #######################
@register('is_liked')
def is_liked(user_id, content_id, content_type):
    like = Like.query.filter(and_(Like.user_id == user_id,
                                  Like.content_id == content_id, Like.content_type == content_type)).first()

    return False if like is None else True

@register('is_collected')
def is_collected(user_id, content_id, content_type):
    collect = Collect.query.filter(and_(Collect.user_id == user_id,
                                  Collect.content_id == content_id, Collect.content_type == content_type)).first()

    return False if collect is None else True


##########  踩和赞 #########
@register('is_voting')
def is_voting(user_id, video_id):
    vote = Vote.query.filter(and_(Vote.user_id == user_id, Vote.video_id == video_id)).first()
    return None if vote is None else vote.type


############  是否购买过  $$$$$$$$$$$$$$$$$$  wtf
@register('is_buyed')
def is_buyed(uid, film_id):
    """ 判断用户是否购买过  """
    if type(film_id) == types.IntType:
        is_buyed = Buy.query.filter(and_(Buy.film_id == film_id, Buy.user_id == uid)).first()
        return False if is_buyed is None else True
    elif type(film_id) == types.ListType:
        buyed_ids = db.session.query(Buy.film_id). \
            filter(and_(Buy.user_id == uid, Buy.film_id.in_(film_id))).all()
        buyed_ids = [b[0] for b in buyed_ids]
        ret_list = [(ret, ret in buyed_ids) for ret in film_id]
        return dict(ret_list)


###########   频道相关  ###########################
@register('get_channel_film_list')
def get_channel_film_list(channel_id, limit=10, offset=0):
    films = Film.query.filter(Film.channel_id == channel_id). \
        order_by(Film.date_create.desc()).limit(limit).offset(offset).all()

    return films


@register('get_channel_film_count')
def get_channel_film_count(channel_id):
    count = Film.query.filter(Film.channel_id == channel_id).count()

    return count


# 标签相关
@register('get_all_tag')
def get_all_tag():
    tags = Tag.query.filter(Tag.show == True).order_by(Tag.id.desc()).all()
    return tags

@register('get_recommend_tag')
def get_recommend_tag(limit=6, offset=0, position=None):

    if not position:
        tags = Tag.query.filter(Tag.recommended == True)
    else:
        tag_ids = RecommendPos.query.get_value(position)
        tags = Tag.query.filter(Tag.id.in_(tag_ids)) if tag_ids else []

    tags = tags.order_by(Tag.order.desc()).limit(limit).offset(0).all() if tags else []

    return tags

@register('get_recommend_tag_count')
def get_recommend_tag_count(limit=6, offset=0, position=None):

    if not position:
        count = Tag.query.filter(Tag.recommended == True).count()
    else:
        count = len(RecommendPos.query.get_value(position))

    return count

@register('get_tag_video_count')
def get_tag_video_count(tag_id, recommended=None):
    # count = Tagmap.query.filter(and_(Tagmap.tag_id==tag_id)).count()
    count = Video.query.join(Tagmap, Video.id == Tagmap.video_id).\
            filter(Tagmap.tag_id == tag_id, Video.show == True)

    if recommended:
        count = count.filter(Video.recommended==True)

    count = count.count()

    return count


@register('get_tag_video')
def get_tag_video(tag_id, offset=0, limit=10, order_type=None, recommended=None):
    videos = Video.query.join(Tagmap, Video.id == Tagmap.video_id). \
        filter(Tagmap.tag_id == tag_id, Video.show == True)

    if recommended:
        videos = videos.filter(Video.recommended==True)

    if order_type=='hottest':
        videos = videos.order_by(Video.play_count.desc())
    else:
        videos = videos.order_by(Video.date_create.desc())

    videos = videos.limit(limit).offset(offset).all()

    return videos

@register('get_tag_video_by_hot')
def get_tag_video_by_hot(tag_id, offset=0, limit=10):
    videos = Video.query.join(Tagmap, Video.id == Tagmap.video_id). \
        filter(Tagmap.tag_id == tag_id, Video.show == True). \
        order_by(Video.play_count.desc()). \
        limit(limit).offset(offset).all()

    return videos

@register('get_tag_video_by_like')
def get_tag_video_by_like(tag_id, offset=0, limit=10):
    videos = Video.query.join(Tagmap, Video.id == Tagmap.video_id). \
        filter(Tagmap.tag_id == tag_id, Video.show == True). \
        order_by(Video.like_count.desc()). \
        limit(limit).offset(offset).all()

    return videos

@register('get_video_tag')
def get_video_tag_name(video_id, offset=0, limit=10):
    tags = Tag.query.join(Tagmap, video_id == Tagmap.video_id). \
        filter(Tag.show == True).order_by(Tag.date_create.desc()).all()

    return tags

@register('_get_tag_id')
def _get_tag_id(tagstr):
    if not tagstr:
        return

    tag = Tag.query.filter(Tag.name == tagstr).first()
    if tag:
        return tag.id
    _tag = Tag(name=tagstr)
    try:
        db.session.add(_tag)
        db.session.commit()
    except:
        pass
    else:
        return _tag.id

    return None

@register('add_video_tag')
def add_video_tag(video_id, tags):
    video_tags = [each_tag.tag_id for each_tag in Tagmap.query.filter(Tagmap.video_id == video_id).all()]

    tags = [each.strip() for each in tags]

    for tag in tags:
        t = _get_tag_id(tag)
        if t is None or t in video_tags:
            continue

        tagmap = Tagmap(video_id=video_id, tag_id=t)
        db.session.add(tagmap)

    try:
        db.session.commit()
    except:
        db.session.rollback()



@register('get_tag_id')
def get_tag_id(tagstr):

    return _get_tag_id(tagstr)



@register('get_tag_live')
def get_tag_live(tag_id, offset=0, limit=10, order_type='hottest', recommended=None):
    lives = Live.query.filter(Live.tag_id == tag_id).filter(Live.status == 'connected')

    if recommended:
        lives = lives.filter(Live.recommended==True)

    if order_type=='hottest':
        lives = lives.order_by(Live.live_user_count.desc())
    else:
        lives = lives.order_by(Live.date_create.desc())

    lives = lives.limit(limit).offset(offset).all()

    return lives


@register('get_tag_live_count')
def get_tag_live_count(tag_id):

    count = Live.query.filter(Live.tag_id == tag_id).\
            filter(Live.status == 'connected').count()

    return count


# 喜欢和取消喜欢
@register('like_content')
def like_content(user_id, content_id, content_type):
    like = Like(user_id=user_id, content_id=content_id, content_type=content_type)

    try:
        db.session.add(like)
        db.session.commit()

        #signals.like_content.send({"like_type":content_type, "content_id":content_id})
    except Exception as error:
        db.session.rollback()
        raise BackendError('InternalError', 'InternalError')
    else:
        if like.id and content_type=="video":
            db.session.query(Video).filter_by(id=content_id).update({'like_count': Video.like_count + 1})
            db.session.commit()
        return like

@register('unlike_content')
def unlike_content(user_id, content_id, content_type):
    re = Like.query.filter(and_(Like.user_id == user_id,
                                  Like.content_id == content_id, Like.content_type == content_type)).delete()
    db.session.commit()

    if re and content_type=="video":
        db.session.query(Video).filter_by(id=content_id).update({'like_count': Video.like_count - 1})
        db.session.commit()


# 搜藏和取消搜藏
@register('collect_content')
def collect_content(user_id, content_id, content_type):
    collect = Collect(user_id=user_id, content_id=content_id, content_type=content_type)

    try:
        db.session.add(collect)
        db.session.commit()

    except Exception as error:
        db.session.rollback()
        raise BackendError('InternalError', 'InternalError')

@register('uncollect_content')
def uncollect_content(user_id, content_id, content_type):
    re = Collect.query.filter(and_(Collect.user_id == user_id,
                                  Collect.content_id == content_id, Collect.content_type == content_type)).delete()
    db.session.commit()



# task 任务相关

@register('get_unreceived_task_count')
def get_unreceived_task_count(user_id):
    count = UserTask.query.filter(and_(UserTask.is_received==False, \
        UserTask.user_id==user_id)).count()

    return count

@register('get_user_exp_rank')
def get_user_exp_rank(exp_value):
    rank = User.query.filter(User.exp_value>exp_value).count()

    return rank + 1

@register('get_exp_rank')
def get_exp_rank(offset=0, limit=10):

    ranks = db.session.query(User, func.row_number().over(order_by='exp_value desc'))

    ranks = ranks.order_by(User.exp_value.desc()).limit(limit).offset(offset).all()

    return ranks

@register('get_user_today_exp')
def get_user_today_exp(user_id):

    exp = db.session.query(func.sum(UserTask.exp_value)). \
        filter(and_(UserTask.is_received==True, UserTask.date_done>=date.today(), \
        UserTask.user_id==user_id)).first()

    return exp[0] or 0

@register('get_user_today_possible_exp')
def get_user_today_possible_exp(user_id):

    exp = db.session.query(func.sum(UserTask.exp_value)). \
        filter(and_(UserTask.is_received==False, UserTask.user_id==user_id)). \
        first()

    return exp[0] or 0

@register('get_tag_like_top')
def get_tag_like_top(tag, date_start, date_end, limit=10):

    tag = Tag.query.filter(Tag.name==tag).first()
    if not tag:
        return []

    videos = Video.query.join(Tagmap, Video.id == Tagmap.video_id). \
        filter(Tagmap.tag_id == tag.id, Video.show == True).all()

    video_dict = {}
    for each_video in videos:

        # _actions = influx_client.query("select * from user_action where \
        #     action_type='like_video' and object_id='%s' and time > '%s' and time < '%s'" % \
        #     (each_video.id, date_start, date_end))['user_action']
        _actions = []

        _set = set()
        for each_action in _actions:
            _set.add(each_action['ip'])

        video_dict[each_video.id] = len(_set)

    re = sorted(video_dict.items(), key=lambda x: x[1], reverse=True)

    return re[:limit]



# @register('vote_film')
# def vote_film(user_id, film_id):
#     vote = Vote(user_id=user_id, film_id=film_id, type='up')
#     try:
#         db.session.add(vote)
#         db.session.commit()
#     except Exception, e:
#         db.session.rollback()
#         vote = None

#     if vote is None:
#         vote = Vote.query.filter(and_(Vote.user_id == user_id, Vote.film_id == film_id)).first()
#         vote.type = 'up'
#         db.session.commit()

#     return vote


# @register('unvote_film')
# def unvote_film(user_id, film_id):
#     vote = Vote.query.filter(and_(Vote.user_id == user_id, Vote.film_id == film_id)).first()
#     if vote:
#         vote.type = 'down'
#         db.session.commit()

#     else:
#         vote = Vote(user_id=user_id, film_id=film_id, type='down')
#         try:
#             db.session.add(vote)
#             db.session.commit()
#         except:
#             db.session.rollback()


# @register('rating_film')
# def rating_film(user_id, film_id, rate):
#     rating = Rating.query.filter(and_(Rating.film_id == film_id, Rating.user_id == user_id)).first()

#     try:
#         if rating is None:
#             rating = Rating(film_id=film_id, user_id=user_id, rate=rate)
#             db.session.add(rating)
#             db.session.commit()
#         else:
#             rating.rate = rate
#             db.session.commit()
#     except:
#         db.session.rollback()
#         raise


# @register('get_user_film_rate')
# def get_user_film_rate(user_id, film_id):
#     rating = Rating.query.filter(and_(Rating.film_id == film_id, Rating.user_id == user_id)).first()
#     return rating.rate if rating else None


@register('get_storage_id')
def get_storage_id(file_md5, file_size):
    storage = Storage()
    storage.md5 = file_md5
    storage.size = file_size
    db.session.add(storage)
    db.session.commit()
    return storage.id


# 根据几个类型返回相对应的数据
@register('get_user_sort')
def get_user_sort(atype):


    date_limit = datetime.now() + timedelta(days=-7)

    user_list = []

    if atype == 'like':

        users = db.session.query(User,func.count(Like.id).label('like_count')).\
                join(Like,User.id == Like.user_id).group_by(User.id).filter(Like.date_create > date_limit).\
                            order_by('like_count desc').limit(20).all()

        for us in users:
            u = us[0].json()
            u.update({'recent_like_count':us[1]})
            user_list.append(u)

    if atype == 'reply':
        users = db.session.query(User,func.count(Reply.id).label('reply_count')).\
            join(Reply,User.id == Reply.creater_id).group_by(User.id).filter(Reply.date_create > date_limit).\
                            order_by('reply_count desc').limit(20).all()

        for us in users:
            u = us[0].json()
            u.update({'recent_reply_count':us[1]})
            user_list.append(u)


    return user_list


@register('get_live_reward_top_list')
def get_live_reward_top_list(user_id,days=-7):


    user_list = db.session.query(Reward.from_id,func.sum(Reward.count).label('reward_count')).\
                    filter(Reward.to_id == user_id)

    if days:
        date_limit = datetime.now() + timedelta(days=-7)
        user_list = user_list.filter(Reward.date_create > date_limit).\
                    group_by(Reward.from_id).order_by('reward_count desc').limit(10).all()
    else:
        user_list = user_list.group_by(Reward.from_id).order_by('reward_count desc').limit(10).all()

    if len(user_list) == 0: return []

    user_ids = [u[0] for u in user_list]


    _users = []

    for u in user_list:
        _u = User.query.get(u[0]).json()
        _u['reward_count'] = u[1]
        _users.append(_u)

    return _users


@register('get_live_list')
def get_live_list(limit=10,offset=0,live='all'):

    if live == 'all':
        lives = Live.query.filter(or_(Live.recommended == True,Live.status == 'connected')).\
            order_by(Live.status.asc(),Live.live_user_count.desc(),Live.date_create.desc()).\
            limit(limit).offset(offset).all()
    else:
        lives = Live.query.filter(Live.status == 'connected').\
            order_by(Live.live_user_count.desc()).\
            limit(limit).offset(offset).all()

    return lives


@register('get_live_list_count')
def get_live_list_count(live='all'):

    if live == 'all':
        count = Live.query.filter(or_(Live.recommended == True,Live.status == 'connected')).count()
    else:
        count = Live.query.filter(Live.status == 'connected').count()

    return count




@register('get_top_user_reward')
def get_top_user_reward(limit=20,offset=0,days=-7):


    user_list = db.session.query(Reward.to_id,func.sum(Reward.count).label('reward_count'))

    if days:
        date_limit = date.today() + timedelta(days=-7)
        user_list = user_list.filter(Reward.date_create > date_limit).\
                    group_by(Reward.to_id).order_by('reward_count desc').\
                    limit(limit).offset(offset).all()
    else:
        user_list = user_list.group_by(Reward.to_id).order_by('reward_count desc').\
                        limit(limit).offset(offset).all()

    if len(user_list) == 0: return []

    user_ids = [u[0] for u in user_list]


    _users = []

    for u in user_list:
        _u = User.query.get(u[0]).json()
        _u['reward_count'] = u[1]
        _users.append(_u)

    return _users


@register('get_top_user_rich')
def get_top_user_rich(limit=20,offset=0,days=-7):


    user_list = db.session.query(Reward.from_id,func.sum(Reward.count).label('reward_count'))

    if days:
        date_limit = date.today() + timedelta(days=-7)
        user_list = user_list.filter(Reward.date_create > date_limit).\
                    group_by(Reward.from_id).order_by('reward_count desc').\
                    limit(limit).offset(offset).all()
    else:
        user_list = user_list.group_by(Reward.from_id).order_by('reward_count desc').\
                        limit(limit).offset(offset).all()

    if len(user_list) == 0: return []

    user_ids = [u[0] for u in user_list]


    _users = []

    for u in user_list:
        _u = User.query.get(u[0]).json()
        _u['reward_count'] = u[1]
        _users.append(_u)

    return _users


#  勤劳榜单
@register('get_top_user_industrious')
def get_top_user_industrious(limit=20,offset=0,days=-7):


    user_list = db.session.query(Live.user_id,func.sum(Live.time).label('live_time'))

    if days:
        date_limit = date.today() + timedelta(days=-7)
        user_list = user_list.filter(Live.date_create > date_limit).\
                    group_by(Live.user_id).order_by('live_time desc').\
                    limit(limit).offset(offset).all()
    else:
        user_list = user_list.group_by(Live.user_id).order_by('live_time desc').\
                        limit(limit).offset(offset).all()

    if len(user_list) == 0: return []

    user_ids = [u[0] for u in user_list]

    _users = []

    for u in user_list:
        _u = User.query.get(u[0]).json()
        _u['live_time'] = u[1]
        _users.append(_u)

    return _users


# 获得某一天的统计数据
@register('get_live_analyze')
def get_live_analyze(user_id,_date):

    date_limit = _date + timedelta(days=1)
    live_time = db.session.query(func.sum(Live.time).label('live_time')).\
                filter(Live.date_create > _date).\
                filter(Live.date_create < date_limit).\
                filter(Live.user_id==user_id).scalar()


    follower_count = Follow.query.filter(Follow.date_create > _date).\
                        filter(Follow.date_create < date_limit).\
                        filter(Follow.user_id_to == user_id).count()


    reward_count = db.session.query(func.sum(Reward.count).label('reward_count')).\
                    filter(Reward.to_id == user_id).\
                    filter(Reward.date_create > _date).\
                    filter(Reward.date_create < date_limit).scalar()


    return {'live_time':live_time,
            'follower_count':follower_count,
            'reward_count':reward_count}


# 获的一个用户总共的数据
@register('get_live_analyze_all')
def get_live_analyze_all(user_id):

    live_time = db.session.query(func.sum(Live.time).label('live_time')).\
                filter(Live.user_id==user_id).scalar()


    follower_count = Follow.query.filter(Follow.user_id_to == user_id).count()


    reward_count = db.session.query(func.sum(Reward.count).label('reward_count')).\
                    filter(Reward.to_id == user_id).scalar()

    return {'live_time':live_time,
            'follower_count':follower_count,
            'reward_count':reward_count}





### signals
# def reply_content(sender):
#     if sender.reply_type == 'post':
#         obj = Post.query.get(sender.post_id)
#         count = Reply.query.filter(and_(Reply.reply_type == 'post',
#                                         Reply.post_id == sender.post_id)).count()
#     elif sender.reply_type == 'review':
#         obj = Review.query.get(sender.post_id)
#         count = Reply.query.filter(and_(Reply.reply_type == 'review',
#                                         Reply.post_id == sender.post_id)).count()
#     elif sender.reply_type == 'note':
#         obj = Note.query.get(sender.post_id)
#         count = Reply.query.filter(and_(Reply.reply_type == 'note',
#                                         Reply.post_id == sender.post_id)).count()
#     else:
#         return

#     obj.comment_count = count

#     db.session.commit()


# def like_content(sender):
#     if sender['content_type'] == 'post':
#         obj = Post.query.get(sender['content_id'])
#     elif sender['content_type'] == 'film':
#         obj = Film.query.get(sender['content_id'])
#     elif sender['content_type'] in ['review', 'short_review']:
#         obj = Review.query.get(sender['content_id'])
#     elif sender['content_type'] == 'note':
#         obj = Note.query.get(sender['content_id'])
#     else:
#         return

#     count = Like.query.filter(and_(Like.content_type == sender['content_type'],
#                                    Like.content_id == sender['content_id'])).count()

#     obj.like_count = count

#     db.session.commit()

def reply_content_handler(sender):

    if sender['reply_type'] == 'video':
        db.session.query(Video).filter_by(id=sender['content_id']).update({'comment_count': Video.comment_count + 1})
        db.session.commit()

    return


def like_content_handler(sender):

    if sender['like_type'] == 'video':
        db.session.query(Video).filter_by(id=sender['content_id']).update({'like_count': Video.like_count + 1})
        db.session.commit()

    return


def update_film_rate(sender):
    film = Film.query.get_or_404(sender)

    film.rate = Rating.query.with_entities(func.avg(Rating.rate).label('average')). \
        filter(Rating.film_id == film.id).scalar()

    db.session.commit()


def add_post(sender):
    group = Group.query.get(sender.group_id)

    if group:
        group.post_count = Post.query.filter_by(group_id=sender.group_id).count()
        db.session.commit()


# signals.rate_update.connect(update_film_rate)
signals.reply_content.connect(reply_content_handler)
signals.like_content.connect(like_content_handler)
# signals.add_post.connect(add_post)
