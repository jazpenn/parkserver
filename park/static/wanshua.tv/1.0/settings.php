<?php include('header.php'); ?>
  <div class="main-content" id="index-content">
    <div class="content page profile-page">
      <div class="content-wrapper">
        <div class="row">
          <div class="col-lg-4 col-md-4 col-sm-12 col-xs-12 settings-sidebar">
            <div class="sidebar-wrapper">
              <h2><i class="fa fa-cog"></i> 设置</h2>
              <ul class="">
                <li class="active"><a href="#">个人设置</a></li>
                <li><a href="settings-password.php">修改密码</a></li>
                <li><a href="settings-billing.php">充值</a></li>
              </ul>
            </div>
          </div>

          <div class="col-lg-8 col-md-8 col-sm-12 col-xs-12 settings-content">
            <div class="settings-content-wrapper">
              <h3>个人设置</h3>
              <form class="form-horizontal">
                <div class="form-group">
                  <label for="user-email" class="col-sm-3 control-label">头像</label>
                  <div class="col-sm-9">
                    <div class="profile-avatar-wrapper">
                      <img src="/assets/placeholder/avatars/11.jpg" class="avatar img-responsive" alt="用户名字">
                      <div class="camera-icon">
                        <div class="camera-icon-wrapper">
                          <input type="file" id="change-avatar" class="avatar-change">
                          <i class="fa fa-camera"></i>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="form-group">
                  <label for="user-email" class="col-sm-3 control-label">账号</label>
                  <div class="col-sm-9">
                    <input type="email" class="form-control" id="user-email" value="abc@example.com" disabled>
                    <p class="form-note">账号邮箱不能修改</p>
                  </div>
                </div>
                <div class="form-group">
                  <label for="user-nickname" class="col-sm-3 control-label">昵称</label>
                  <div class="col-sm-9">
                    <input type="text" class="form-control" id="user-nickname" value="巴拉巴拉小魔仙" placeholder="昵称">
                    <p class="form-note form-note-error">昵称不能为空</p> <!-- 提交为空时出现 -->
                  </div>
                </div>
                <div class="form-group">
                  <label for="user-gender" class="col-sm-3 control-label">性别</label>
                  <div class="col-sm-9">
                    <div class="radio">
                      <label>
                        <input type="radio" name="usergender" id="user-male" value="male" checked>
                        男
                      </label>
                    </div>
                    <div class="radio">
                      <label>
                        <input type="radio" name="usergender" id="user-female" value="female">
                        女
                      </label>
                    </div>
                  </div>
                </div>
                <!-- <div class="form-group">
                  <label for="user-weibo" class="col-sm-3 control-label">微博</label>
                  <div class="col-sm-9">
                    <span>@巴拉巴拉小魔仙</span>
                    <a href="#"><small>解除绑定</small></a>
                  </div>
                </div>
                <div class="form-group">
                  <label for="user-wechat" class="col-sm-3 control-label">微信</label>
                  <div class="col-sm-9">
                    <a href="#"><small>绑定微信</small></a>
                  </div>
                </div> -->
                <div class="form-group">
                  <div class="col-sm-offset-3 col-sm-9">
                    <button type="submit" class="btn btn-success">保存设置</button>
                  </div>
                </div>
              </form>

            </div>
          </div>
        </div>
      </div>
      <?php include('template-parts/footer-main.php'); //引入全局底部信息 ?>
    </div>

  </div>

<?php include('footer.php'); ?>