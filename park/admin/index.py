# -*- coding: utf-8 -*-
# author: notedit

import sys
import time
import json
import flask
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

from park.extensions import db

from park import authutil, strutil
from park.models.models import User, CmsUser, RecommendPos, Video, User, Channel, Tag

from .forms import BannerListForm

from . import instance


# @instance.route('/index_banner', methods=['GET', 'POST'])
# @authutil.admin_user_required
# def index_banner():
#     pos = RecommendPos.query.filter_by(name='index-banner-list').first()

#     if pos is None: return 'index-banner-list should not be none'

#     id_list = json.loads(pos.content)

#     content_str = ','.join(map(str, id_list))

#     form = BannerListForm(content=content_str)

#     if form.validate_on_submit():
#         content = form.content.data

#         id_list = content.split(',')
#         id_list = [int(_id) for _id in id_list if _id]

#         pos.content = json.dumps(id_list)

#         db.session.commit()

#     videos = Video.query.filter(Video.id.in_(id_list)).all()

#     return render_template('admin/index_banner.html',
#                            form=form,
#                            videos=videos
#     )


@instance.route('/index_test', methods=['GET', 'POST'])
@authutil.admin_user_required
def index_test():
    
    # user_ids = request.values.get('user_ids')
    #
    # if user_ids:
    #     user_ids = user_ids.split(',')
    #
    #     User.__table__.update(bind=db.engine).values({'recommended': False}).\
    #         where(User.__table__.c.recommended==True).execute()
    #     User.__table__.update(bind=db.engine).values({'recommended': True}).\
    #         where(User.__table__.c.id.in_(user_ids)).execute()
    #
    # users = User.query.filter(User.recommended==True).all()

    return render_template('admin/index.html',
                           # users=users
    )

