# -*- coding: utf-8 -*-
# author: leeoxiang

import types
import time
import json
import random
import hashlib
import contextlib
from datetime import datetime
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
from sqlalchemy import Column, DateTime, Text, Boolean, Sequence, Integer, \
    String, PickleType, MetaData, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM, ARRAY, Any, All
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy import desc, asc
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.sqlalchemy import BaseQuery
from flask import current_app
from park.extensions import db
from park.helpers import BackendError, register, assert_error
from .models import RecommendPos, User, Video,\
    Group, Follow, Reply, Post, Watch, Message, Action, Like, Notify, UserAlias, Collect,\
    Live


# ------ Define ------


def _is_follow_(self, user):

    if not user:
        return False

    return is_follow_user(uid=user.id, uid_to=self.id)


User.is_follow = _is_follow_


# ------- API ------


@register('get_user_info')
def get_user_info(user_id, json=False):
    """user_id can be int or a list"""
    multi = False
    if type(user_id) == types.ListType:
        assert_error(
            all([type(u) == types.IntType for u in user_id]), 'ParamError')
        multi = True
    else:
        user_id = user_id,

    users = User.query.filter(User.id.in_(user_id)).all()
    if len(users) == 0:
        raise BackendError('EmptyError', '用户不存在')

    if multi:
        return [user.to_json() for user in users] if json else users
    else:
        return users[0].to_json() if json else users[0]


@register('get_user_follower')
def get_user_follower(uid, limit=50, offset=0):
    assert_error(offset >= 0, 'ParamError')
    follower = User.query.join(Follow, User.id == Follow.user_id). \
        filter(and_(Follow.user_id_to == uid, Follow.user_id != Follow.user_id_to)).order_by(
            Follow.date_create.desc()).limit(limit).offset(offset).all()
    return follower


@register('get_user_follower_count')
def get_user_follower_count(uid):
    count = Follow.query.filter(
        and_(Follow.user_id_to == uid, Follow.user_id != Follow.user_id_to)).count()
    return count


@register('get_user_like_list')
def get_user_like_list(user_id, offset=0, limit=10):
    assert_error(offset >= 0, 'ParamError')
    videos = Video.query.filter(Video.show == True).join(Like, Video.id == Like.content_id).\
        filter(Like.user_id == user_id).\
        order_by(Like.date_create.desc()).\
        limit(limit).offset(offset).all()

    return videos


@register('get_user_like_count')
def get_user_like_count(user_id):
    count = Like.query.filter(Like.user_id == user_id).join(
        Video, Video.id == Like.content_id).filter(Video.show == True).count()
    return count


@register('get_user_collect_list')
def get_user_collect_list(user_id, offset=0, limit=10):
    assert_error(offset >= 0, 'ParamError')
    videos = Video.query.filter(Video.show == True).join(Collect, Video.id == Collect.content_id).\
        filter(Collect.user_id == user_id).\
        order_by(Collect.date_create.desc()).\
        limit(limit).offset(offset).all()

    return videos


@register('get_user_collect_count')
def get_user_collect_count(user_id):
    count = Collect.query.filter(Collect.user_id == user_id).join(
        Video, Video.id == Collect.content_id).filter(Video.show == True).count()
    return count


@register('get_user_following')
def get_following_user(uid, limit=50, offset=0, all=False):
    assert_error(offset >= 0, 'ParamError')
    followed_user = User.query.join(Follow, User.id == Follow.user_id_to). \
        filter(and_(Follow.user_id == uid, Follow.user_id != Follow.user_id_to)).order_by(
            Follow.date_create.desc()).limit(limit).offset(offset).all()
    return followed_user


@register('get_user_following_count')
def get_user_following_count(uid):
    count = Follow.query.filter(
        and_(Follow.user_id == uid, Follow.user_id != Follow.user_id_to)).count()
    return count


# 得到用户关注的正在的直播
@register('get_user_following_live')
def get_following_live(uid, limit=50, offset=0):
    assert_error(offset >= 0, 'ParamError')
    followed_user = User.query.join(Follow, User.id == Follow.user_id_to). \
        filter(and_(Follow.user_id == uid, Follow.user_id != Follow.user_id_to)).order_by(
            Follow.date_create.desc()).limit(limit).offset(offset).all()

    if len(followed_user) == 0:
        return []

    user_ids = [u.id for u in followed_user]

    lives = Live.query.filter(Live.user_id.in_(user_ids)).filter(
        Live.status == 'connected').all()

    return lives


@register('is_follow_user')
def is_follow_user(uid, uid_to):
    """判断用户是否关注"""
    is_followed = Follow.query.filter(
        and_(Follow.user_id == uid, Follow.user_id_to == uid_to)).first()
    return False if is_followed is None else True


@register('follow_user')
def follow_user(uid, uid_to):
    follow = Follow(user_id=uid, user_id_to=uid_to)
    try:
        db.session.add(follow)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        raise BackendError('InternalError', 'InternalError')


@register('unfollow_user')
def unfollow_user(uid, uid_to):
    follow = Follow.query.filter(
        and_(Follow.user_id == uid, Follow.user_id_to == uid_to)).first()
    if follow is not None:
        db.session.delete(follow)
        db.session.commit()


# 获得给某个用户的留言
@register('get_user_message_list')
def get_user_message_list(user_id, offset=0, limit=20):
    messages = Message.query.filter_by(user_id_to=user_id).order_by(Message.date_create.desc()). \
        limit(limit).offset(offset).all()
    return messages


@register('get_user_message_count')
def get_user_message_count(user_id):
    count = Message.query.filter_by(user_id_to=user_id).count()
    return count


@register('get_user_by_uid')
def get_user_by_uid(uid):
    ua = UserAlias.query.filter(UserAlias.open_id == uid).first()

    if ua is None:
        raise BackendError('EmptyError', '用户不存在')
    else:
        return User.query.get(ua.user_id)


@register('get_user_by_username')
def get_user_by_username(username):

    user = User.query.filter_by(username=username).first()

    return user


@register('set_user')
def set_user(user_id, info):
    user = User.query.get(user_id)

    try:
        for k, v in info.items():
            if v is not None:
                setattr(user, k, v)
        db.session.commit()
    except:
        db.session.rollback()
        raise
    else:
        return user


@register('get_user_alias_list')
def get_user_alias_list(user_id):
    alias_list = UserAlias.query.filter_by(user_id=user_id).all()
    return alias_list


@register('set_user_alias')
def set_user_alias(user_id, _type, open_id, access_token):

    alias_value = {
        "open_id": open_id,
        "access_token": access_token,
        "user_id": user_id,
        "type": _type,
    }

    try:
        db.session.add(UserAlias(**alias_value))
        db.session.commit()
    except Exception as error:
        return False

    return True


@register('unset_user_alias')
def unset_user_alias(user_id, alias_type):

    alias_count = UserAlias.query.filter_by(user_id=user_id).count()

    if alias_count == 1:
        return False

    result = db.session.query(UserAlias).filter(
        UserAlias.user_id == user_id, UserAlias.type == alias_type).delete()
    db.session.commit()

    return bool(result)


@register('is_common_follow')
def is_common_follow(user_id, user_id_to):

    query = db.session.query(Follow).filter(and_(Follow.user_id == user_id,
                                                 Follow.user_id_to == user_id_to)).exists()

    query_ = db.session.query(Follow).filter(and_(Follow.user_id == user_id_to,
                                                  Follow.user_id_to == user_id)).exists()

    re = db.session.query(query, query_).first()

    return all(re)

# ############### 用户动态相关  #######################

"""
action_type:



'new_video'
'like_video'

"""

ACTION_TYPE = ['new_video', 'like_video']


@register('add_newaction')
def add_newaction(info):
    """ 添加新的模板 """
    assert_error(info['action_type'] in ACTION_TYPE, 'ParamError')

    action = Action(**info)

    db.session.add(action)
    db.session.commit()

    return action.id


@register('get_user_action')
def get_user_action(user_id, offset=0, limit=30):
    actions = Action.query.filter(Action.user_id == user_id). \
        order_by(Action.date_create.desc()).limit(limit).offset(offset).all()
    return actions


@register('get_user_action_count')
def get_user_action_count(user_id):
    count = Action.query.filter(Action.user_id == user_id).count()

    return count


def _get_following_user_ids(user_id):
    user_ids = db.session.query(Follow.user_id_to).filter(
        Follow.user_id == user_id).all()
    return [u[0] for u in user_ids]


@register('get_follow_action')
def get_follow_action(user_id, offset=0, limit=30):
    following_user = _get_following_user_ids(user_id)
    following_user.extend([user_id])

    # 添加一个默认的账号
    following_user.extend([913656144621208724])

    actions = Action.query.filter(Action.user_id.in_(following_user)).order_by(Action.date_create.desc()). \
        limit(limit).offset(offset).all()

    count = Action.query.filter(Action.user_id.in_(following_user)).count()

    return actions, count


#################### 用户提醒相关  如果使用 hstore 性能会好一些#######################


"""  notify 验证 以后考虑加上
class PushValid:
    @classmethod
    def check(cls, extra):
        return all([func(extra) for func in cls.check_funs])

class PushReplyValid(PushValid):
    check_funs = [
        lambda extra: extra.has_key('reply_id') and type(extra['reply_id']) in (types.IntType, types.LongType),
        lambda extra: extra.has_key('date_create') and type(extra['date_create']) in (types.IntType, types.LongType),
    ]

class PushFollowUserValid(PushValid):
    check_funs = [
        lambda extra: extra.has_key('ukey_from') and type(extra['ukey_from']) == types.StringType and len(extra['ukey_from']) == 6,
        lambda extra: extra.has_key('date_create') and type(extra['date_create']) in (types.IntType, types.LongType),
    ]

class PushAtValid(PushValid):
    check_funs = [
        lambda extra: extra.has_key('ukey_from') and type(extra['ukey_from']) == types.StringType and len(extra['ukey_from']) == 6,
        lambda extra: extra.has_key('reply_id') and type(extra['reply_id']) in (types.IntType, types.LongType),             ## 如果是在主贴里at的话， 这里可以为-1
        lambda extra: extra.has_key('date_create') and type(extra['date_create']) in (types.IntType, types.LongType),
    ]

"""


# 推入一个新的提醒
@register('push_notify')
def push_notify(user_to, notify_type, user_from, **kwarg):
    """
    需要统一的写一套 valid
    """
    if notify_type == 'follow_user':
        data = dict(user_to=user_to,
                    notify_type=notify_type,
                    user_from=user_from)

    if notify_type == 'reply_video':
        data = dict(user_to=user_to,
                    notify_type=notify_type,
                    user_from=user_from,
                    content_id=kwarg['content_id'],
                    reply_id=kwarg['reply_id'])

    if notify_type == 'like_video':
        data = dict(user_to=user_to,
                    notify_type=notify_type,
                    user_from=user_from,
                    content_id=kwarg['content_id'])

    if notify_type == 'reply_reply':
        data = dict(user_to=user_to,
                    notify_type=notify_type,
                    user_from=user_from,
                    content_id=kwarg['content_id'],
                    reply_id=kwarg['reply_id'])

    notify = Notify(**data)
    db.session.add(notify)
    db.session.commit()

    return notify


@register('get_notify_list')
def get_notify_list(user_id, is_readed=False, notify_type=None, limit=10, offset=0):

    notifys = Notify.query.order_by(Notify.is_readed).\
        order_by(Notify.date_last_update.desc()).filter(
            Notify.user_to == user_id)

    if is_readed == False:
        notifys = notifys.filter(Notify.is_readed == False)

    if notify_type:
        if notify_type == 'reply':
            notifys = notifys.filter(or_(Notify.notify_type == 'reply_video',
                                         Notify.notify_type == 'reply_reply'))
        else:
            notifys = notifys.filter(Notify.notify_type == notify_type)

    if limit:
        notifys = notifys.limit(limit)

    if offset:
        notifys = notifys.offset(offset)

    notifys = notifys.all()

    return notifys


@register('get_notify_list_count')
def get_notify_list_count(user_id, is_readed=False, notify_type=None):

    notifys = Notify.query.filter(Notify.user_to == user_id)

    if is_readed == False:
        notifys = notifys.filter(Notify.is_readed == False)

    if notify_type:
        if notify_type == 'reply':
            notifys = notifys.filter(or_(Notify.notify_type == 'reply_video',
                                         Notify.notify_type == 'reply_reply'))
        else:
            notifys = notifys.filter(Notify.notify_type == notify_type)

    count = notifys.count()

    return count


SQL_NOTIFY_UPDATE_READED = """UPDATE notify SET is_readed='t' WHERE %(wheres)s"""


@register('set_notify_readed')
def set_notify_readed(query):
    """
    设置某个人的所有提醒为已读  则提供 {'user_id':xxx}
    设置某人的关于某条提醒为已读  则提供{'notify_id':xxx}
    """

    qk = query.keys()

    wheres = ['is_readed=%s' % repr('f'), ]

    for k in qk:
        v = query[k]
        if k == 'user_id':
            wheres.append('user_to = %s' % str(v))
        elif k == 'notify_id':
            wheres.append('id = %s' % repr(v))

    sql = SQL_NOTIFY_UPDATE_READED % {'wheres': ' AND '.join(wheres)}

    print(sql)

    res = db.session.execute(sql)
    db.session.commit()
    return res
