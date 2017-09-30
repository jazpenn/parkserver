# -*- coding: utf-8 -*-

import os
import sys
import time
import hmac
import datetime
import hashlib
from hashlib import sha1, md5

from functools import wraps

from park import strutil

from flask import jsonify, url_for

from flask import g, request, redirect, session

from flask import current_app as app

from park.models.models import User


ERR_DICT = {
        1:'ok',
        404:'请求不存在',
        500:'服务端出错了',
        10000: u'参数错误',
        10001: u'服务出错啦',
        10002: u'没有权限',
        10003: u'需要登陆',
        10004: u'操作过于频繁',
        10005: u'绑定失败,该账号已被绑定',
        10006: u'解绑失败,每个账号至少绑定一个第三方账号',
        10007: u'更新失败,该用户名已存在',
        10008: u'更新失败,更新内容过长或不合法',
        10009: u'您的账户已被冻结, 请联系客服',
        10010: u'您还没有经过直播认证,请加qq群294147440申请直播认证',
        10011: u'您的信仰值已经不够,请充值',
        10012: u'不要给自己充值啦，么么哒',
        10013: u'验证码不匹配',
        10014: u'手机号已经绑定过另外一个账号',
        10015: u'手机号和密码不符',
        10016: u'手机号没有注册过用户',
        10017: u'用户名已经被占用,如果是老用户请在玩耍直播观看端个人页面进绑定',
        10018: u'你还没有绑定过手机',
        10019: u'需要重新登陆',
        10020: u'短信验证码发送失败',
        10021: u'未到领取奖励的时间',
        10022: u'已经领取过玩耍币',
        10023: u'房间无法匹配',
        10024: u'红包已经被抢完',
        10025: u'不要发布重复的内容',
        10026: u'今日观看奖励已经领取完毕，明天再来(⊙o⊙)哦'
        }

def apijson(*args,**kwargs):

    _data = dict(*args,**kwargs)

    if _data.get('code'):
        code = _data.pop('code')
    else:
        code = 1

    err_message = ERR_DICT[code]

    return jsonify(code=code,data=_data,err_message=err_message)







def _cookie_digest(payload, key=None):
    if key is None:
        key = app.config['SECRET_KEY']
    payload = payload.encode('utf-8')
    mac = hmac.new(key, payload, sha1)
    return mac.hexdigest()


def encode_cookie(payload):
    return u'%s|%s' % (payload, _cookie_digest(payload))


def decode_cookie(cookie):
    try:
        payload, digest = cookie.rsplit(u'|', 1)
        digest = digest.encode('ascii')
    except ValueError:
        return None

    if _cookie_digest(payload) == digest:
        return payload
    else:
        return None


def set_logined(req, resp, ukey, timeout=None):
    kargs = {
        'path': '/', 'secure': None
    }
    date_create = int(time.time())
    if timeout is not None:
        assert isinstance(timeout, (int, long)), 'timeout must be an integer or None'
        kargs['max_age'] = timeout
        kargs['expires'] = strutil.cookie_date(date_create + timeout)
    else:
        timeout = 0
    date_create = str(date_create)
    sha1sum = hashlib.sha1(app.config.get('SECRET_KEY', '') + ukey + date_create).hexdigest()
    resp.set_cookie('ukey', encode_cookie(ukey), **kargs)
    resp.set_cookie('date_create', encode_cookie(date_create), **kargs)
    resp.set_cookie('token', sha1sum, **kargs)


def set_logout(resp):
    resp.delete_cookie('ukey')
    resp.delete_cookie('date_create')
    resp.delete_cookie('token')


def is_logined(req):
    ukey = decode_cookie(req.cookies.get('ukey', u''))
    date_create = decode_cookie(req.cookies.get('date_create', u''))
    if not (ukey and date_create):
        return False
    token = req.cookies.get('token', '')
    if sha1(app.config.get('SECRET_KEY') + ukey.encode('utf-8') + \
            date_create.encode('utf-8')).hexdigest() == token:
        return True
    return False


# ########################################################################

def login(user):
    session['curr_id'] = user.id
    session['name'] = user.username
    session['email'] = user.email


def logout():
    sessdata = dict(session)
    for key in sessdata.keys():
        del session[key]


def user_required(f):
    '''必须登陆后才能访问的视图'''

    def decorator(*args, **kwargs):
        if not session.get('curr_id'):
            next = request.url if g.keep_login_url else None
            return redirect(url_for('web.login', next=next))
        return f(*args, **kwargs)

    decorator.__name__ = f.__name__
    return decorator


def api_user_required(f):
    def decorator(*args, **kwargs):
        if not session.get('curr_id'):
            return api_error(errnum=300, errmsg=u'还没有登录')
        return f(*args, **kwargs)

    decorator.__name__ = f.__name__
    return decorator

def not_frozen_required(f):
    def decorator(*args, **kwargs):
        if g.user.status == 'blocked':
            return api_error(errnum=403, errmsg=u'用户已被冻结')
        return f(*args, **kwargs)

    decorator.__name__ = f.__name__
    return decorator

def admin_user_required(f):
    def decorator(*args, **kwargs):
        if not g.user:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)

    decorator.__name__ = f.__name__
    return decorator


def api_error(errnum, errmsg):
    return jsonify(errnum=errnum, errmsg=errmsg)


########### 为移动端api 准备的 ############


def api_auth(f):
    @wraps(f)
    def func(*args, **kargs):
        token = request.headers.get('token') or \
                request.values.get('token') or (request.json and request.json.get('token'))

        if token is None:
            return apijson(code=10003)

        try:
            user = User.query.filter_by(token=token).first_or_404()
        except:
            return apijson(code=10019)

        g.user = user
        return f(*args, **kargs)

    return func


def is_authed():
    token = request.headers.get('token') or \
            request.values.get('token') or (request.json and request.json.get('token') )

    if token is None:
        return False

    try:
        user = User.query.filter_by(token=token).first_or_404()
    except:
        return False

    g.user = user

    return True

def api_not_frozen_required(f):
    def decorator(*args, **kwargs):
        if g.user.status == 'blocked':
            return apijson(code=10009)
        return f(*args, **kwargs)

    decorator.__name__ = f.__name__
    return decorator
