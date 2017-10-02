from flask import Blueprint
from flask import request
from flask import Blueprint
from flask import g
from park.models.models import User, CmsUser
from park import authutil

instance = Blueprint('admin', 'admin')


from . import admin, index


@instance.before_request
def cookie_auth():
    g.clean = False
    if authutil.is_logined(request):
        try:
            user_id = int(
                authutil.decode_cookie(request.cookies.get('ukey', u'')))
            g.user = CmsUser.query.get(user_id)
        except:
            raise
            g.clean = True
            g.user = {}

    else:
        g.user = {}