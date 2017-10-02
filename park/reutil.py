# -*- coding: utf-8 -*-

from park.extensions import influx_client, redis
from datetime import timedelta
from datetime import datetime
from uuid import uuid1
import pickle

"""
redis_util::ip_map
"""

IP_MAP = 'IP_MAP'
IP_MAP_LEN = 'IP_MAP_LEN'

IP_MAP_EXPIRE_TIME = 'IP_MAP_EXPIRE_TIME'

expire_time = None

def do_ip_map(ip, _timedelta=timedelta(hours=1)):

    global expire_time

    ip_map_key = 'ip::' + ip

    ip_value = redis.hget(IP_MAP, ip_map_key)
    if ip_value:
        return ip_value

    ip_value = redis.incr(IP_MAP_LEN)
    if redis.exists(IP_MAP):
        redis.hset(IP_MAP, ip_map_key, ip_value)
        return ip_value

    redis.hset(IP_MAP, ip_map_key, ip_value)
    expire_time = datetime.now() + _timedelta
    redis.set(IP_MAP_EXPIRE_TIME, pickle.dumps(expire_time))
    redis.expireat(IP_MAP, expire_time)
    redis.expireat(IP_MAP_LEN, expire_time)
    return ip_value

"""
do_key_ip_map
"""
def do_key_ip_map(key, ip):

    global expire_time

    ip_value = do_ip_map(ip)

    is_existed = redis.getbit(key, ip_value)
    if is_existed:
        return True

    if redis.exists(key):
        redis.setbit(key, ip_value, 1)
        return False

    expire_time = expire_time or pickle.loads(redis.get(IP_MAP_EXPIRE_TIME))
    redis.setbit(key, ip_value, 1)
    redis.expireat(key, expire_time)
    return False


"""
redis_util::hot_rank
"""
class RedisRank(object):
    """docstring for RedisRank"""
    def __init__(self, base_redis_key, time_delta, time_strf,
            expire_time=timedelta(days=7), cache_time=timedelta(seconds=300)):
        super(RedisRank, self).__init__()
        self.base_redis_key = base_redis_key
        self.expire_time = expire_time
        self.cache_time = cache_time
        self.time_delta = time_delta
        self.time_strf = time_strf

        self.rank_key = ':'.join(['redis_rank_result', self.base_redis_key])

        self._sets = redis.keys(':'.join(['redis_rank', self.base_redis_key, '*']))

    def write(self, sort_key, increment=1):
        
        redis_key = self.generate_redis_key(_datetime=datetime.now())

        re = redis.zincrby(redis_key, sort_key, increment)

        if float(re)==increment and redis_key not in self._sets:
            redis.expire(redis_key, self.expire_time)
            self._sets.append(redis_key)

        return re

    def generate_redis_key(self, _datetime):
        redis_key = ':'.join(['redis_rank', self.base_redis_key,\
            _datetime.strftime(self.time_strf)])

        return redis_key

    def generate_redis_key_list(self, timedelta_num):
        
        now_datetime = datetime.now()

        return [ self.generate_redis_key(now_datetime-self.time_delta*i)\
            for i in range(timedelta_num) ]

    def get_rank(self, start, stop, timedelta_num, desc=True):

        rank_key = self.rank_key + ':' + str(timedelta_num)

        rank_result_key = self.rank_key + ':' + ':'.join([str(start), str(stop),\
            str(timedelta_num), str(desc)])

        re = redis.get(rank_result_key)

        if re:
            re = pickle.loads(re)
        else:
            re = redis.zrange(rank_key, start, stop, withscores=True, desc=desc)
            if re:
                redis.setex(rank_result_key, self.cache_time, pickle.dumps(re))
            else:
                set_key_list = self.generate_redis_key_list(timedelta_num)

                redis.zunionstore(rank_key, set_key_list)

                redis.expire(rank_key, self.cache_time)

                re = redis.zrange(rank_key, start, stop, withscores=True, desc=desc)

                redis.setex(rank_result_key, self.cache_time, pickle.dumps(re))

        return re

# # Global RedisRank

# VideoHotRank = RedisRank(base_redis_key='video_hot_rank', time_delta=timedelta(days=1),\
#                     time_strf='%m-%d', expire_time=timedelta(days=12))

# UserHotRank = RedisRank(base_redis_key='user_hot_rank', time_delta=timedelta(days=1),\
#                     time_strf='%m-%d', expire_time=timedelta(days=38))

# UserActivityRank = RedisRank(base_redis_key='user_activity_rank', time_delta=timedelta(days=1),\
#                     time_strf='%m-%d', expire_time=timedelta(days=3))
