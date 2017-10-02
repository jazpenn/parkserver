# -*- coding: utf-8 -*-
# author: notedit

import sys
import time
import flask
import uuid
from datetime import date
from datetime import datetime
from datetime import timedelta
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
from flask import url_for
from sqlalchemy import func as function
from sqlalchemy import desc, asc
from sqlalchemy.sql import select
from sqlalchemy.sql import and_, or_, not_
from werkzeug.security import generate_password_hash, check_password_hash
from park.extensions import db
from park import authutil, strutil
from park.models.models import User, CmsUser, Video, Reply
from . import instance, func
from .forms import LoginForm

from park.extensions import influx_client


@instance.route('/')
@instance.route('/index')
def index():
    print('访问首页')
    if authutil.is_logined(request):
        print('登录认证成功')

        date_limit = date.today()

        # today_video_count = Video.query.filter(Video.date_create>date_limit).count()
        # today_reply_count = Reply.query.filter(Reply.date_create>date_limit).count()
        # today_user_count = User.query.filter(User.date_create>date_limit).count()
        #
        # all_user_count = User.query.count()
        # all_uploaded_user_count = User.query.join(Video).distinct().count()
        #
        # all_video_count = Video.query.count()
        # all_available_video_count = Video.query.filter(Video.show==True).count()

        yesterday = date_limit + timedelta(days=-1)

        yesterday_mobile_play_count = 0

        # try:
        #     today_mobile_play_count = influx_client.query("select sum(value) from user_action where \
        #         action_type='watch_video' and _from='mobile' and time > '%s' " % str(date_limit))['user_action']. \
        #         next()['sum']
        # except StopIteration:
        today_mobile_play_count = 0

        return render_template('admin/index.html',
                            # today_video_count=today_video_count,
                            # today_reply_count=today_reply_count,
                            # today_user_count=today_user_count,
                            # all_user_count=all_user_count,
                            # all_uploaded_user_count=all_uploaded_user_count,
                            # all_video_count=all_video_count,
                            # all_available_video_count=all_available_video_count,
                            # yesterday_mobile_play_count=yesterday_mobile_play_count,
                            # today_mobile_play_count=today_mobile_play_count
                            )
    print('登录认证失败,即将跳到登录')
    return redirect(url_for('.login'))


@instance.route('/test', methods=["GET", ])
def test():
    print(session.get('user_id'))
    return "hello tester"


@instance.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('.index'))

    form = LoginForm()

    if form.validate_on_submit():

        email = form.email.data
        password = form.password.data
        #print(email)

        cms_user = CmsUser.query.filter(CmsUser.email == email).first()
        print('用户:', cms_user)
        if cms_user is None:
            #print('hahahahah')
            flash('user does not exist', 'error')
            return render_template('admin/login.html', form=form)

        if not check_password_hash(cms_user.password, password):
            print('验证出错了')
            flash('user does not exist', 'error')
            return render_template('admin/login.html', form=form)

        resp = redirect(url_for('.index'))

        authutil.set_logined(request, resp, str(cms_user.id), 3600 * 24 * 90)

        return resp

    return render_template('admin/login.html',
                           form=form
    )


@instance.route('/logout')
def logout():
    resp = redirect(url_for('.index'))

    authutil.set_logout(resp)

    return resp
