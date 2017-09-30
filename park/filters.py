# -*- coding: utf-8 -*-

from re import findall
from datetime import datetime
from datetime import timedelta
from flask import session, current_app
from park.extensions import db, redis
#from park.models import backend
# from park.models.models import User
#from park.cacheutil import rcache

from park import strutil

"""
filter里面用到的缓存  要有相应的清除操作
"""

# ####  for inner use


# def is_liked(user_id, content_id, content_type):
#     return backend.is_liked(user_id, content_id, content_type)


# def is_voting(user_id, video_id):
#     return backend.is_voting(user_id, video_id)


#####


HOUR_FILTER = 3600 * 13
_today = lambda: datetime(*datetime.now().timetuple()[:3])


def format_datetime(date_time):
    time_delta = datetime.now() - date_time

    time_delta = time_delta.total_seconds()

    if time_delta < HOUR_FILTER:
        if time_delta < 60:
            timeoffset = u'刚刚'
        elif time_delta < 3600:
            timeoffset = u'%d分钟前' % (time_delta / 60)
        else:
            timeoffset = u'%d小时前' % (time_delta / 3600)
        return timeoffset

    today = _today()

    if date_time >= today:
        timeoffset = u'今天'
    elif date_time > (today + timedelta(days=-1)):
        timeoffset = u'%d天前' % ( time_delta / 86400 + 1 )
    else:
        timeoffset = date_time.strftime('%Y-%m-%d')
    return timeoffset


def strcut(s, length=200, killwords=False):
    if s is None:
        return ''
    if not isinstance(s, unicode):
        s = s.decode('utf-8')

    if len(s) > length:
        s = s[:length] + '...'
    return s


# 定义全局的图片域名
def img_path(img_name):
    #return img_name

    if not img_name:
        return ''

    return current_app.config["VIDEO_PIC_URL"] + img_name + "-tiny"


# #半个小时的缓存
# @rcache(1800)
# def follower_count(uid):
#     uid = strutil.b57decode(uid)
#     return backend.get_user_follower_count(uid)


# @rcache(1800)
# def user_video_count(uid):
#     uid = strutil.b57decode(uid)
#     return backend.get_user_video_count(uid)


# def islike(content_id):
#     if not content_id:
#         return False
#     if session.get('curr_id') is None:
#         return False
#     return is_liked(session['curr_id'], content_id, 'video')


# def isfollow(uid):
#     if not uid:
#         return False

#     if session.get('curr_id') is None:
#         return False

#     return  backend.is_follow_user(session.get('curr_id'),uid)

# def voting(film_id):
#     """
#     有三种结果  'up','down' or  None
#     """
#     if not film_id:
#         return None
#     if session.get('curr_id') is None:
#         return None
#     return is_voting(session['curr_id'], film_id)


# 把数据库里的Video.rate给算成0到5之间的评价数
# def parse_rating(rate):
#     def parse_rating_recursive(parsed, to_parse):
#         if to_parse is None:
#             return parsed
#         elif to_parse <= 0.25:
#             return parsed
#         else:
#             return parse_rating_recursive(parsed + 0.5, to_parse - 0.5)


#     return parse_rating_recursive(0, None if rate is None else (10 * rate) / 2)


# # 根据评价数得到size为5的list，这个list用来render星星
# # 比如1.5会算出[1,0.5,0,0,0]，模板会用这个list渲染一颗半星加上三颗半空星
# def parse_stars(rate):
#     def extract_stars(extracted, to_extract):
#         if to_extract is None:
#             return extracted
#         elif to_extract < 0.5:
#             return extracted
#         elif to_extract >= 1:
#             extracted.append(1)
#             return extract_stars(extracted, to_extract - 1)
#         else:
#             extracted.append(0.5)
#             return extract_stars(extracted, to_extract - 0.5)


#     def add_zero_stars_upto(stars, upto):
#         if len(stars) == upto:
#             return stars
#         elif len(stars) < upto:
#             stars.append(0)
#             return add_zero_stars_upto(stars, upto)
#         else:
#             # 需要的话这里可以改一下
#             stars.pop()
#             return add_zero_stars_upto(stars, upto)


#     return add_zero_stars_upto(extract_stars([], rate), 5)


# ##### 下方施工重地！！
# # 默认从database得到的数据是以{时间}{{分隔符}{时间}}+的格式存在的
# # 下面函数就是把这个如此卧槽的数据加工成正常人能看明白的数据链表
# # 当然你也可以要求与原始数据一致的结果
# def parse_time_components_from_database(from_database, readable=True):
#     # 原来这个参数是datatime.datetime对象。。。
#     # raise Exception('type of from_database: ', type(from_database))
#     components = findall(r"[\d']+", from_database)  # 换法子吧 这块要改改
#     if readable:
#         return components[:-1]  # 砍掉反人类的末位数据
#     else:
#         return components


# # 从时间成分链表(time_comps)中选择需要的时间成分(用comps_selector)并渲染()
# def select_comps():
#     pass


# def render_time(time_comps, comps_selector, renderer):
#     return renderer(comps_selector(time_comps))


# # 更新：好像看到另一个函数做类似的功能了 = = 待修正或砍掉
# # 不知道会不会需要 感觉有一天会需要 先写一下 = =
# def parse_date(raw_data):
#     def templates():
#         return ["{0}年",
#                 "{0}月",
#                 "{0}日",
#                 "{0}时",
#                 "{0}分",
#                 "{0}秒"]


#     def render_component(temp, time):
#         return temp.format(time)


#     def render_date(temps, times):
#         return ''.join(map(render_component, temps, times))


#     return render_date(templates(),
#                        parse_time_list(raw_data))


# def extract_year_month_day(raw_data):
#     return "{y}-{m}-{d}".format(y=raw_data.year,
#                                 m=raw_data.month,
#                                 d=raw_data.day)


# def extract_hour_minute(raw_data):
#     return "{h}:{m}".format(h=raw_data.hour,
#                             m=raw_data.minute)


##### 上方施工重地！！


def format_time(timestr):
    try:
        time_int = int(timestr)
    except:
        return '未知'

    _str = ''
    left, second = time_int / 60, time_int % 60

    if left:
        hour, minite = left / 60, left % 60
        if hour:
            _str = u'{0}时{1}分{2}秒'.format(hour, minite, second)
        else:
            _str = u'{0}分{1}秒'.format(minite, second)
    else:
        _str = u'{0}秒'.format(second)

    return _str


def format_times(timestr):
    time_str = str(timestr)
    new_time = findall('\d{4}-\d{2}-\d{2}',time_str)[0]
    return new_time[0:4]+'年'+new_time[5:7]+'月'+new_time[-2:]+'日'

# # 更新：这个可能不需要用到，待修正
# # 模板里可以用这个把获取的视频链表分割成几块再一块块渲染
# # stackoverflow.com/a/312467/2430571
# import itertools


# def split_seq_gen(iterable, size):
#     it = iter(iterable)
#     item = list(itertools.islice(it, size))
#     while item:
#         yield item
#         item = list(itertools.islice(it, size))


# # 更新：这个也待修正
# # 也可能会需要有个list版本的
# def split_seq(iterable, size):
#     return [item for item in split_seq_gen(iterable, size)]


def render_gender(raw_gender_data):
    if type(raw_gender_data) == bool:
        if raw_gender_data == True:
            return "女"
        else:
            return "男"
    elif raw_gender_data == None:
        return "未知"
    else:
        return type(raw_gender_data)

def new_render_gender(raw_gender_data):

    if raw_gender_data==1:
        return '男'
    elif raw_gender_data==2:
        return '女'
    else:
        return '未知'


# def following_count(uid):
#     uid = strutil.b57decode(uid)
#     return backend.get_user_following_count(uid)

# def user_like_count(uid):
#     uid = strutil.b57decode(uid)
#     return backend.get_user_like_count(uid,'video')

def to_uid(_id):
    return strutil.b57encode(_id)

register_filters = {
    'format_datetime': format_datetime,
    'format_time': format_time,
    # 'extract_year_month_day': extract_year_month_day,
    # 'extract_hour_minute': extract_hour_minute,
    'strcut': strcut,
    # 'follower_count': follower_count,
    # 'following_count': following_count,
    # 'video_count': user_video_count,
    # 'like_count': user_like_count,
    # 'islike': islike,
    # 'isfollow':isfollow,
    # 'parse_rating': parse_rating,
    # 'parse_stars': parse_stars,
    # 'voting': voting,
    'img_path': img_path,
    #'split_seq': split_seq,
    # 'range': range,  #ugly!!
    # 'len': len,  #ugly!!
    'render_gender': render_gender,
    'new_render_gender': new_render_gender,
    'to_uid': to_uid,
    'format_times':format_times
}
