# -*- coding: utf-8 -*-
import re
import os
import sys
import time
import datetime
import math
import hashlib
import base64
import random
import json

import requests

from email.utils import formatdate

from flask import abort, current_app

from qiniu import Auth, set_default, PersistentFop, build_op, op_save
from qiniu import put_data, put_file, put_stream
from qiniu import BucketManager

from park.extensions import redis
from PIL import Image
import upyun

ACCESS_KEY = '9wLPqikPvlXdOWkC4SKTPSHbLCWORMXtipkya0GZ'
SECRET_KEY = 'hZCdW1Nih9i40dxo0kLG68GjT50JTXc3lz_reT_Y'

auth = Auth(ACCESS_KEY, SECRET_KEY)
bucket = BucketManager(auth)


month_ago = lambda: int(time.time()) - 2592000


def safe_int(int_str, default=0):
    try:
        return int(int_str)
    except Exception as error:
        return default


def cookie_date(epoch_seconds=None):
    rfcdate = formatdate(epoch_seconds)
    return '%s-%s-%s GMT' % (rfcdate[:7], rfcdate[8:11], rfcdate[12:25])


def get_xxx_rand():
    return str(random.randint(0, 10)) + str(random.randint(0, 10)) + str(random.randint(0, 10))


def int2path(uint, baseurl, extname=''):
    """将32bit正整数转换为path"""
    file_key = ''
    for i in range(6):
        uint, remainder = divmod(uint, 36)
        if remainder < 10:
            file_key = chr(remainder + 48) + file_key
        else:
            file_key = chr(remainder + 97 - 10) + file_key

    fullurl = os.path.join(
        baseurl, file_key[0:2], file_key[2:4], file_key[4:6], file_key + extname)
    return fullurl


def int2ukey(uint):
    ukey = ''
    for i in range(6):
        uint, remainder = divmod(uint, 36)
        if remainder < 10:
            ukey = chr(remainder + 48) + ukey
        else:
            ukey = chr(remainder + 97 - 10) + ukey
    return ukey


def oct_buffer(buf):
    retstr = ''.join(map(lambda c: '\\\\%03o' % ord(c), buf))
    retstr = "E'" + retstr + "'"
    return retstr


def hex_buffer(buf):
    retstr = ''.join(map(lambda c: '\\x%02x' % ord(c), buf))
    retstr = "E'" + retstr + "'"
    return retstr


img_regex = re.compile(
    r'\S+\.(jpg|png|gif|jpeg|bmp)$', re.IGNORECASE)

url_regex = re.compile(
    r'^https?://'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

match_mention = re.compile(r'([^@\S]+)@([\w\u4e00-\u9fcb\u3400-\u4db5.-]{1,20})')


def parse_mentions(strs):
    mentions = [matchobj.group(2) for matchobj in match_mention.finditer(strs)]
    return set(mentions)


def is_image_url(url):
    return url is not None and img_regex.search(url)


def is_valid_url(url):
    return url is not None and url_regex.search(url)


def get_page_num(req):
    try:
        page = int(req.values.get('page', 1))
    except:
        page = 1
    else:
        if page < 1:
            abort(404)

    return page


def pager(page_num, tol_count, base_url, where='', per_page=25, nav_len=7):
    '''
    分页相关的代码
    page_num : 当前页码
    tol_count: 对象总数
    base_url: 当前页面的url
    per_page: 每页显示对象数
    nav_len: 显示的分页个数
    '''
    qd = {'base_url': base_url, 'num': '', 'where': where}
    if tol_count <= per_page:
        return ''
    if page_num == 1:
        prev_li_str = '<li class="disabled"><a href="#"><i class="icon-angle-left">&laquo;</i></a></li>\n'
    else:
        qd['num'] = page_num - 1
        prev_li_str = '<li><a href="%(base_url)s?page=%(num)s%(where)s"><i class="icon-angle-left">&laquo;</i></a></li>\n' % qd

    page_count = (tol_count + per_page - 1) / per_page
    if page_num == page_count:
        next_li_str = '<li class="disabled"><a href="#"><i class="icon-angle-right">&raquo;</i></a></li>\n'
    else:
        qd['num'] = page_num + 1
        next_li_str = '<li><a href="%(base_url)s?page=%(num)s%(where)s"><i class="icon-angle-right">&raquo;</i></a></li>\n' % qd

    nav_len = nav_len / 2
    page_start = page_num - nav_len if (page_num - nav_len) > 1 else 1
    page_end = page_num + nav_len + 1 if page_num + \
        nav_len <= page_count else page_count + 1
    page_range = range(page_start, page_end)
    if len(page_range) > 0 and page_range[0] != 1:
        page_range.insert(0, -1)
    if len(page_range) > 0 and page_range[-1] != page_count:
        page_range.append(-1)

    middle_line = []
    for num in page_range:
        if num == -1:
            middle_line.append(
                '<li class="disabled"><a href="#">...</a></li>\n')
        elif num == page_num:
            middle_line.append(
                '<li class="active"><a href="#">%d</a></li>\n' % num)
        else:
            qd['num'] = num
            qd['shownum'] = num
            middle_line.append(
                '<li><a href="%(base_url)s?page=%(num)s%(where)s">%(shownum)s</a></li>\n' % qd)

    html = '<ul class="pagination">%s%s%s</ul>\n' % (
        prev_li_str,
        ''.join(middle_line),
        next_li_str,
    )
    return html


def make_thumb(path):
    """
    sizes 参数传递要生成的尺寸，可以生成多种尺寸
    """
    base, ext = os.path.splitext(path)
    try:
        im = Image.open(path)
    except IOError:
        print(' in  IOError')
        return
    mode = im.mode
    if mode not in ('L', 'RGB'):
        if mode == 'RGBA':
            # 透明图片需要加白色底
            im.load()
            alpha = im.split()[3]
            bgmask = alpha.point(lambda x: 255 - x)
            im = im.convert('RGB')
            # paste(color, box, mask)
            im.paste((255, 255, 255), None, bgmask)
        else:
            im = im.convert('RGB')

    iwidth, iheight = im.size  # pixels
    # make sure your "limiter" is the denominator
    size_proportion = iheight / float(iwidth)
    newheight = size_proportion * 170

    thumb = im.resize((170, int(newheight)), Image.ANTIALIAS)
    # thumb = im.thumbnail((170,170), Image.ANTIALIAS)
    thumb.save(path, quality=100)  # 默认


def make_thumb_crop(path, x, y, w, h):
    im = Image.open(path)
    basepath = os.path.splitext(path)[0]
    filename170 = basepath + '_170.jpg'
    filename50 = basepath + '_50.jpg'

    x2 = int(round(float(x)))
    y2 = int(round(float(y)))
    w2 = int(round(float(w)))
    h2 = int(round(float(h)))

    box = (x2, y2, x2 + w2, y2 + h2)

    region = im.crop(box)
    thumb170 = region.resize((170, 170), Image.ANTIALIAS)
    thumb50 = region.resize((50, 50), Image.ANTIALIAS)
    thumb170.save(filename170, quality=85)
    thumb50.save(filename50, quality=85)

    return filename170, filename50


def hashcompat():
    """
    The md5 and sha modules are deprecated since Python 2.5, replaced by the
    hashlib module containing both hash algorithms. Here, we provide a common
    interface to the md5 and sha constructors, preferring the hashlib module when
    available.
    """

    try:
        import hashlib

        md5_constructor = hashlib.md5
        md5_hmac = md5_constructor
        sha_constructor = hashlib.sha1
        sha_hmac = sha_constructor
    except ImportError:
        import md5

        md5_constructor = md5.new
        md5_hmac = md5
        import sha

        sha_constructor = sha.new
        sha_hmac = sha

    return md5_constructor


def writeFile(file_url, file_md5, file_data):
    fullpath = file_url
    dirname = os.path.dirname(fullpath)
    if not os.path.exists(dirname):
        os.makedirs(dirname, 0o700)

    with open(fullpath, 'wb') as f:
        f.write(file_data)
        f.flush()
    return fullpath


def upyun_upload(file_id, file_data, file_md5, basepath='/storage', extname='.png'):
    if current_app.config.get('CONFIG_TYPE') == 'production':
        upyun.bucket = 'bq-storage'
    else:
        upyun.bucket = 'bq-storage-test'
        basepath = basepath + '_test'

    file_url = int2path(file_id, basepath, extname=extname)

    upyun.setContentMD5(file_md5)
    ret = upyun.writeFile(file_url, file_data, True)
    return file_url


def upyun_upload_file(file_url, ffile):
    if current_app.config.get('CONFIG_TYPE') == 'production':
        upyun.bucket = 'biquu-storage'
    else:
        upyun.bucket = 'biquu-storage-test'

    ret = upyun.writeFile(file_url, ffile, True)
    return ret


def generate_upload_token():
    return auth.upload_token('tinvideo')


def generate_upload_token_image():
    return auth.upload_token('tinimage')


def generate_upload_token_avatar():
    return auth.upload_token('tinavatar')


def generate_upload_vframe_op(save_key, offset=0, width=None, height=None):

    vframe_ops = {'offset': offset}

    if width:
        vframe_ops['w'] = width
    if height:
        vframe_ops['h'] = height

    op = build_op('vframe', 'png', **vframe_ops)

    return op_save(op, 'tinimage', save_key + '.png')


def generate_upload_avthumb_op(save_key, width_height=(1280, 720)):

    avthumb_ops = {
        'ab': '128k',
        'ar': 44100,
        'acodec': 'libfaac',
        'vb': '1m',
        'vcodec': 'libx264',
        'stripmeta': 0,
        #'rotate':'auto',#_rotate
        'wmImage': base64.urlsafe_b64encode('http://7rfgxc.com2.z0.glb.qiniucdn.com/water_mark.png'),
        'wmGravity': 'NorthEast'
    }

    if width_height:
        avthumb_ops['s'] = '%dx%d' % width_height
        avthumb_ops['autoscale'] = 1

    op = build_op('avthumb', 'mp4', **avthumb_ops)

    return op_save(op, 'tin-encode-video', save_key + '.mp4')


def qiniu_upload(file_key, localfile):

    token = generate_upload_token()

    ret, info = put_file(token, file_key + '.mp4', localfile)

    print("======")
    print(time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime()))
    print(ret)
    print(info)
    print("======")

    pfop = PersistentFop(auth, 'tinvideo')

    ret, info = pfop.execute(
        file_key + '.mp4', [generate_upload_vframe_op(file_key), generate_upload_avthumb_op(file_key)], 1)

    print("======")
    print(time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime()))
    print(ret)
    print(info)
    print("======")


def qiniu_video_encode(file_key):

    pfop = PersistentFop(auth, 'tinvideo', 'videoencode')

    ret, info = pfop.execute(file_key, [generate_upload_vframe_op(
        file_key), generate_upload_avthumb_op(file_key)], 1)

    print("======")
    print(time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime()))
    print(ret)
    print(info)
    print("======")


def qiniu_upload_image(file_key, localfile):

    token = generate_upload_token_image()

    ret, info = put_file(token, file_key + '.jpg', localfile)

    print("======")
    print(time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime()))
    print(ret)
    print(info)
    print("======")


def qiniu_upload_image_stream(file_key, _file):

    token = generate_upload_token_image()

    print(_file.mimetype)

    ret, info = put_data(token, file_key + '.jpg', _file.stream.read(),
                         mime_type=_file.mimetype, check_crc=True)

    print("======")
    print(time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime()))
    print (ret)
    print(info)
    print("======")


def now_time():
    return get_time(60 * 60 * 8)


def ytd_time():
    return get_time((60 * 60 * 8) - (3600 * 24))


def get_time(times):
    createValue = time.time() + times
    createValue = float(createValue)
    return time.strftime('%Y-%m-%d', time.gmtime(createValue)) + ' 00:00:00'


import binascii
import math
import os


class ShortUID(object):

    def __init__(self, alphabet=None):
        if alphabet is None:
            alphabet = list("23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
                            "abcdefghijkmnopqrstuvwxyz")
        # Define our alphabet.
        self._alphabet = alphabet
        self._alpha_len = len(self._alphabet)

    def _num_to_string(self, number, pad_to_length=None):
        """
        Convert a number to a string, using the given alphabet.
        """
        output = ""
        while number:
            number, digit = divmod(number, self._alpha_len)
            output += self._alphabet[digit]
        if pad_to_length:
            remainder = max(pad_to_length - len(output), 0)
            output = output + self._alphabet[0] * remainder
        return output

    def _string_to_int(self, string):
        """
        Convert a string to a number, using the given alphabet..
        """
        number = 0
        for char in string[::-1]:
            number = number * self._alpha_len + self._alphabet.index(char)
        return number

    # @staticmethod
    # def unexpected_char_callback():
    #     """
    #     Abort 404, when get unexpected_char
    #     """
    #     abort(404)

_global_instance = ShortUID()
b57encode = _global_instance._num_to_string
b57decode = _global_instance._string_to_int


from Crypto.Cipher import AES


class Encryptor(object):

    """the encryptor that base on PyCrypto"""

    @staticmethod
    def aes_256_encode(text):
        text = text.encode()
        aes_secret = current_app.config.get('AES_SECRET')
        aes_obj = AES.new(hashlib.md5(aes_secret).hexdigest())
        text_length = (len(text)/16+1)*16
        b16_text = '%%%ds' % text_length % text
        encrypted_text = aes_obj.encrypt(b16_text)
        return base64.b16encode(encrypted_text)

    @staticmethod
    def aes_256_decode(text):

        if (len(text) % 16 != 0):
            return None

        aes_secret = current_app.config.get('AES_SECRET')
        aes_obj = AES.new(hashlib.md5(aes_secret).hexdigest())
        text = base64.b16decode(text)
        return aes_obj.decrypt(text).strip()


def generate_access_token(user_info, expire_time):

    token_info = 'access_token::%s::%s' % (user_info, time.time()+expire_time)

    access_token = Encryptor.aes_256_encode(token_info)

    return access_token


def check_access_token(access_token):

    access_token = Encryptor.aes_256_decode(access_token)

    uid, expire_time = access_token.split('::')[1:]

    if uid == g.user.uid and time.time() <= float(expire_time):
        return True
    return False


def generate_live_user(count):

    print('count', count)
    if count <= 0:
        count = 3
    _count = 3
    rand = random.randint(1, count)
    if count < 5:
        _count = count * 4 + rand
    elif count >= 5 and count < 10:
        _count = count * 8 + rand
    elif count >= 10 and count < 20:
        _count = int(count * 16) + rand
    elif count >= 20 and count < 50:
        _count = int(count * 20) + rand
    elif count >= 50 and count < 100:
        _count = int(count * 30) + rand
    elif count >= 100 and count < 200:
        _count = int(count * 40) + rand
    elif count >= 200:
        _count = int(count * 50) + rand

    return _count + random.randint(90,105)


def push_message(room, message, data):

    base_url = 'http://101.200.144.186/pub?id=' + str(room)


    #base_url = 'http://182.92.152.61:9080/pub?id=' + str(room)


    _data = json.dumps({message: data})

    res = requests.post(base_url, data=_data)

    print(res.text)



def generate_hongbao(total_money,total_people,min_money=10):

    _list = []

    i = 0
    while (i<total_people-1):
        j = i + 1
        safe_money =  (total_money - (total_people - j) * min_money) / (total_people - j)

        tmp_money = (random.random() * (safe_money * 100 - min_money * 100) + min_money * 100) / 100

        tmp_money = int(tmp_money)

        total_money = total_money - tmp_money

        _list.append(tmp_money)

        i += 1

    _list.append(int(total_money))

    return _list


def push_room_message(room,message):

    key = 'ROOM::%s::HISTORY' % str(room)

    pip = redis.pipeline()
    pip.lpush(key,message)
    pip.ltrim(key,0,9)

    pip.execute()


def get_room_message(room):

    key = 'ROOM::%s::HISTORY' % str(room)

    _list = redis.lrange(key,0,-1)

    if len(_list) == 0:

        return []

    _chats = []

    _list.reverse()

    for l in _list:
        _l = json.loads(l)
        _chats.append(_l)

    return _chats


def filter_content(user_id,content):

    content_key = 'USER::%s::CHAT' % str(user_id)

    ret = redis.getset(content_key,content)

    if ret == content:
        return True

    return False
