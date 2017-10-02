<?php include('header.php'); ?>
  <div class="main-content" id="index-content">
    <div class="content page profile-page">
      <div class="content-wrapper">
        <div class="row">

          <div class="col-lg-8 col-lg-offset-2 col-md-8 col-md-offset-2 col-sm-12 col-xs-12 settings-content">
            <div class="settings-content-wrapper log-in-out" id="form-account">
              <h3><span>忘记密码</span></h3>

              <!-- 登录失败提示 -->
              <div class="alert alert-info" role="alert">
                <i class="fa fa-info-circle"></i> 请输入手机号获取验证码，以重设密码。
              </div>

              <form class="form-horizontal form-account">
                <div class="form-group phone-number">
                  <div class="input-group">
                    <input type="phone" class="form-control" id="user-phone" placeholder="您的手机号">
                     <div class="input-group-addon">
                      <a href="#" id="validate-btn">获取验证码</a>
                      <!-- <span id="validate-countdown hide">59 秒后重新获取</span> -->
                     </div>
                  </div>
                  <div class="form-note form-note-error">
                    请输入正确的手机号
                  </div>
                </div>

                <div class="form-group">
                  <div class="">
                    <input type="number" class="form-control" id="user-code" placeholder="输入手机验证码">
                  </div>
                </div>

                <div class="form-group">
                  <div class="">
                    <input type="password" class="form-control" id="user-password" placeholder="输入密码">
                  </div>
                </div>

                <div class="form-group">
                  <div class="">
                    <button type="submit" class="form-control btn btn-success">重设密码</button>
                  </div>
                </div>
              </form>
            </div>
            <div class="form-account-add">
              <a href="#" class="pull-left">&laquo; 登录</a>
              <a href="#" class="pull-right">注册账号 &raquo;</a>
            </div>
          </div>
        </div>
      </div>

      <?php include('template-parts/footer-main.php'); //引入全局底部信息 ?>
    </div>

  </div>

<?php include('footer.php'); ?>