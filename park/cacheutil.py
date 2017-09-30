# -*- coding: utf-8 -*-
# File: cacheutil.py
# Author: leeoxiang<leeoxiang@gmail.com>

import types
import time
import hashlib
import json
import pickle

from flask import current_app

from .extensions import redis


def rcache(timeout, cachekey=None, unless=None):
    """基于redis 的函数调用缓存"""
    def inter1(func):
        def inter2(*args, **kwargs):
            if callable(unless) and unless() is True:
                return func(*args, **kwargs)

            if cachekey is not None:
                callstr = cachekey
            else:
                params = map(lambda xx: str(xx), args)
                for (k, v) in kwargs.items():
                    params.append('%s=%s' % (k, str(v)))
                callstr = 'CALLCACHE::%s(%s)' % (func.func_name, ','.join(params))
            retobj = redis.get(callstr)
            if retobj:
                return pickle.loads(retobj)
            retobj = func(*args, **kwargs)
            redis.setex(callstr, timeout, pickle.dumps(retobj))
            return retobj

        inter2.__name__ = func.__name__
        return inter2

    return inter1


# def delete_cache(func, *args, **kwargs):
#     """用相同的参数删除rcache"""
#     if not callable(func):
#         raise DeprecationWarning("Deleting messages by relative name is no longer"
#                                  " reliable, please switch to a function reference")

#     try:
#         if 'cachekey' in kwargs.keys():
#             callstr = kwargs['cachekey']
#         else:
#             params = map(lambda xx: str(xx), args)
#             for (k, v) in kwargs.items():
#                 params.append('%s=%s' % (k, str(v)))
#             callstr = 'CALLCACHE::%s(%s)' % (func.func_name, ','.join(params))
#         print callstr
#         redis.delete(callstr)
#     except Exception, e:
#         raise

def func_redis_cache(timeout=300):
    def handle_func(func):
        def handle_argvs(*args, **kwargs):

            redis_key = ':'.join([func.__name__, str(args), str(kwargs)])

            re_value = redis.get(redis_key)
            if re_value:
                return pickle.loads(re_value)

            re_value = func(*args, **kwargs)

            redis.setex(redis_key, timeout, pickle.dumps(re_value))

            return re_value

        handle_argvs.__name__ = func.__name__
        return handle_argvs

    return handle_func


def ugc_control_set(user_id, obj_type, obj_id, timeout):
    """
    设置UGC的时间
    可以在执行ugc操作之前先过来set 一下,如果返回True则允许下一步
    False则因为太频繁不允许ugc
    """
    assert type(user_id) == types.LongType
    assert type(timeout) == types.IntType
    q = {
        'user_id': user_id,
        'obj_type': obj_type,
        'obj_id': obj_id
    }
    _key = """UGC::%(user_id)s::%(obj_type)s::%(obj_id)s""" % q
    ret = redis.get(_key)
    if ret != None:
        return False
    else:
        redis.setex(_key, timeout, 'on')
        return True

