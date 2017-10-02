<!-- 登录失败提示 -->
<div class="alert alert-danger" role="alert">
  <i class="fa fa-info-circle"></i> 账号或密码错误，请重试！
</div>

<form class="form-horizontal form-account">
  <div class="form-group phone-number">
    <div class="input-group">
      <input type="phone" class="form-control" v-model='phone' id="user-phone" placeholder="您的手机号">
    </div>
    <!-- <div class="form-note form-note-error">
      请输入正确的手机号
    </div> -->
  </div>
  <div class="form-group">
    <div class="">
      <input type="password" class="form-control" id="user-password" placeholder="输入密码">
    </div>
  </div>
  <div class="form-group">
    <div class="">
      <button type="submit" class="form-control btn btn-success">登录</button>
    </div>
  </div>
</form>