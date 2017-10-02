# -*- coding: utf-8 -*-
# author: notedit

import sys
import time
import flask
from hashlib import sha1, md5
from flask import Blueprint
from flask import request
from flask import g
from flask import redirect
from flask import flash
from flask import render_template
from flask import Response
from flask import current_app
from flask import session
from flask import jsonify
from flask import abort

from sqlalchemy import func
from sqlalchemy import desc, asc
from sqlalchemy.sql import select
from sqlalchemy.sql import and_, or_, not_

from park.extensions import redis, db, cache

from park import authutil, strutil
from park.models import backend

#from park.decorators import keep_login_url

from park.models.models import User

# from park.cacheutil import rcache

#from .profile import pipe_load

from . import instance


@instance.route('/')
@instance.route('/index')
def index_new():

    #recommend_users = backend.get_user_recommend_list(limit=10,offset=0)

    limit = 20

    #lives = backend.get_live_list(limit=limit,offset=0)


    return render_template('index_new.html',
                        #recommend_users=recommend_users,
                        #lives=lives
           )



@instance.route('/index/loadmore')
def index_loadmore():

    page = strutil.get_page_num(request)


    limit = 20
    offset = (page - 1) * limit

    lives = backend.get_live_list(limit=limit,offset=offset)

    _lives = []

    for l in lives:

        _l = l.json()
        _l['user'] = l.user.json()
        _lives.append(_l)


    return jsonify(lives=_lives,page=page)




@instance.route('/test')
def test():
    return "hello tester"


@instance.route('/about')
def about():
    return render_template('page_about.html')


@instance.route('/contact')
def contact():
    return render_template('page_contact.html')

