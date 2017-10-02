# -*- coding: utf-8 -*-

#from flask.ext.wtf import Form
from flask.ext.wtf import FlaskForm as Form
from wtforms import IntegerField, HiddenField, BooleanField, TextField, PasswordField, SubmitField, TextField, ValidationError
from wtforms.validators import required, email, equal_to, regexp

USERNAME_RE = r'^[\w.+_]+$'

is_username = regexp(USERNAME_RE, message=u'用户名只允许字母,数字,下划线')


class LoginForm(Form):
    email = TextField(validators=[email(u'邮箱格式不正确')])
    password = PasswordField(validators=[required(u'密码不能为空')])
    remember = TextField()


class BannerListForm(Form):
    content = TextField()


class JPushForm(Form):
    alert = TextField()
    title = TextField()
    recmd_type = TextField()
    time_to_live = TextField()
    relating_info = TextField()


class EditTagForm(Form):
    id = TextField()
    name = TextField()
    pic_url = TextField()
    type = TextField()
    order = TextField()
    introduction = TextField()
    re_path = TextField()


class EditReviewForm(Form):
    id = TextField()
    title = TextField()
    content = TextField()
    re_path = TextField()
    date_update = TextField()


class EditCriticApplyForm(Form):
    id = TextField()
    user_id = TextField()
    realname = TextField()
    phone = TextField()
    email = TextField()
    organization = TextField()
    contact = TextField()
    date_create = TextField()


class EditNoteForm(Form):
    id = TextField()
    title = TextField()
    creater_id = TextField()
    content = TextField()
    film_id = TextField()
    show = TextField()
    recommended = TextField()
    comment_count = TextField()
    like_count = TextField()
    date_create = TextField()
    date_update = TextField()
    re_path = TextField()


class EditUserForm(Form):
    id = TextField()
    username = TextField()
    nickname = TextField()
    email = TextField(validators=[email(u'邮箱格式不正确')])
    password = PasswordField(validators=[required(u'密码不能为空')])
    avatar_big = TextField()
    avatar_small = TextField()
    avatar = TextField()
    gender = BooleanField()
    new_gender = IntegerField()
    status = BooleanField()
    type = TextField()
    introduction = TextField()
    balance = TextField()
    review_recommend = BooleanField()
    note_recommend = BooleanField()
    date_create = TextField()
    date_update = TextField()
    re_path = TextField()


class EditReplyForm(Form):
    id = TextField()
    content = TextField()
    creater_id = TextField()
    reply_type = TextField()


class EditGroupForm(Form):
    id = TextField()
    name = TextField()
    introduction = TextField()
    abstract = TextField()
    creater_id = TextField()
    date_update = TextField()
    pic_small = TextField()
    pic_big = TextField()
    img_url = TextField()
    date_update = TextField()
    re_path = TextField()


class EditPostForm(Form):
    id = TextField()
    title = TextField()
    content = TextField()
    date_update = TextField()
    show = TextField()
    re_path = TextField()
    recommended = TextField()


class EditFilmForm(Form):
    id = TextField()
    rate = TextField()
    show = TextField()
    price = TextField()
    title = TextField()
    actor = TextField()
    creater_id = TextField()
    url = TextField()
    director = TextField()
    recommended = TextField()
    introduction = TextField()
    date_update = TextField()
    re_path = TextField()
    pic_small = TextField()
    pic_big = TextField()
    img_url = TextField()
    company = TextField()
    time = TextField()
    tmp_tag = TextField()
    re_path = TextField()
    tmp_tagids = TextField()


class EditGameForm(Form):
    name = TextField()
    package_name = TextField()
    game_pic = TextField()
    ios_url = TextField()
    android_url = TextField()
    description = TextField()
    show = TextField()


class EditVideoForm(Form):
    id = TextField()
    rate = TextField()
    show = TextField()
    title = TextField()
    tags = TextField()
    url = TextField()
    type = TextField()
    recommended = TextField()
    introduction = TextField()
    date_update = TextField()
    video_pic = TextField()
    img_url = TextField()
    time = TextField()
    channel_id = TextField()
    re_path = TextField()
    creater_id = TextField()
    game_id = TextField()


class EditLiveForm(Form):
    id = TextField()
    title = TextField()
    game_id = TextField()
    user_id = TextField()
    room_id = TextField()
    time  = TextField()
    snapshot = TextField()
    video_url = TextField()
    show = BooleanField()
    recommended = BooleanField()
    phone_model = TextField()


class EditChannelForm(Form):
    id = TextField()
    channel_name = TextField()
    pic_url = TextField()
    show = TextField()
    #is_channel = TextField()
    type = TextField()
    relating_info = TextField()
    order = TextField()
    date_create = TextField()
    is_banner = TextField()
    re_path = TextField()
    game_id = TextField()

class EditVersionForm(Form):
    id = TextField()
    version_name = TextField()
    version_type = IntegerField()
    version_log = TextField()
    version_url = TextField()
    version_date = TextField()
    re_path = TextField()
