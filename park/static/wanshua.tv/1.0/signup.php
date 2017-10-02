<?php include('header.php'); ?>
  <div class="main-content" id="index-content">
    <div class="content page profile-page">
      <div class="content-wrapper">
        <div class="row">

          <div class="col-lg-8 col-lg-offset-2 col-md-8 col-md-offset-2 col-sm-12 col-xs-12 settings-content">
            <div class="settings-content-wrapper log-in-out" id="form-account">
              <h3><span>注册新账号</span></h3>

              <?php include('macros/form-signup.php'); //引入注册表单 ?>

              <?php include('macros/social-login.php'); //引入社交登录 ?>

            </div>
            <div class="form-account-add">
              <a href="#" class="pull-left">&laquo; 忘记密码？</a>
              <a href="#" class="pull-right">注册账号 &raquo;</a>
            </div>
          </div>
        </div>
      </div>

      <?php include('template-parts/footer-main.php'); //引入全局底部信息 ?>
    </div>

  </div>

<?php include('footer.php'); ?>