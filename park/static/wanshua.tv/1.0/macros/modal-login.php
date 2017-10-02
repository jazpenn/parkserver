<div class="modal fade" id="modal-login" tabindex="-1" role="dialog">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <ul class="nav nav-tabs" role="tablist">
            <li role="presentation" class="active"><a href="#modal-signin" aria-controls="modal-signin" role="tab" data-toggle="tab">登录</a></li>
            <li role="presentation"><a href="#modal-signup" aria-controls="modal-signup" role="tab" data-toggle="tab">注册</a></li>
          </ul>
        </div>
        <div class="modal-body log-in-out">

          <div class="tab-content">

            <!-- 登录 Tab -->
            <div role="tabpanel" class="tab-pane active" id="modal-signin">
              <?php include('macros/form-login.php'); //引入登录表单 ?>
            </div>

            <!-- 注册 Tab -->
            <div role="tabpanel" class="tab-pane" id="modal-signup">
              <?php include('macros/form-signup.php'); //引入注册表单 ?>
            </div>

          </div>

          <?php include('macros/social-login.php'); //引入社交登录 ?>

          <div class="form-account-add">
            <a href="forgotpwd.php" title="忘记密码">忘记密码？</a>
          </div>
        </div>
      </div><!-- /.modal-content -->
    </div><!-- /.modal-dialog -->
  </div>