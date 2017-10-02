
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        {% for type,message in messages %}
            <!-- 登录失败提示 -->
            <div class="alert alert-danger" role="alert">
              <i class="fa fa-info-circle"></i> {{ message }}
            </div>
        {% endfor %}
    {% endif %}
{% endwith %}

<form class="form-horizontal form-account" action="/user/signup" method="POST">
  <div class="form-group phone-number">
    <div class="input-group">
      <input type="phone" name="phone" class="form-control" id="user-phone" placeholder="您的手机号">
       <div class="input-group-addon">
        <a href="#" id="validate-btn" @click="send_code">获取验证码</a>
        <!-- <span id="validate-countdown hide">59 秒后重新获取</span> -->
       </div>
    </div>
    <!-- <div class="form-note form-note-error">
      请输入正确的手机号
    </div> -->
  </div>

  <div class="form-group">
    <div class="">
      <input type="number" name="code" class="form-control" id="user-code" placeholder="输入手机验证码">
    </div>
  </div>

  <div class="form-group">
    <div class="">
      <input type="password" name="password" class="form-control" id="user-password" placeholder="输入密码">
    </div>
  </div>

  <div class="form-group">
    <div class="">
      <button type="submit" class="form-control btn btn-success">注册新账号</button>
    </div>
  </div>
</form>