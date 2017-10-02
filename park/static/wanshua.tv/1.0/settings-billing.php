<?php include('header.php'); ?>
  <div class="main-content" id="index-content">
    <div class="content page profile-page">
      <div class="content-wrapper">
        <div class="row">
          <div class="col-lg-4 col-md-4 col-sm-12 col-xs-12 settings-sidebar">
            <div class="sidebar-wrapper">
              <h2><i class="fa fa-cog"></i> 设置</h2>
              <ul class="">
                <li><a href="settings.php">个人设置</a></li>
                <li><a href="settings-password.php">修改密码</a></li>
                <li class="active"><a href="settings-billing.php">充值</a></li>
              </ul>
            </div>
          </div>

          <div class="col-lg-8 col-md-8 col-sm-12 col-xs-12 settings-content">
            <div class="settings-content-wrapper">
              <h3>充值</h3>
              <form class="form-horizontal bill-selection">
                <div class="form-group">
                  <div class="radio bill-count">
                    <input type="radio" name="user-bill" id="bill-5" value="5" checked>
                    <label for="bill-5">
                      5元=300 玩耍币
                    </label>
                  </div>
                  <div class="radio bill-count">
                    <input type="radio" name="user-bill" id="bill-10" value="10">
                    <label for="bill-10">
                      10元=1000 玩耍币
                    </label>
                  </div>
                  <div class="radio bill-count">
                    <input type="radio" name="user-bill" id="bill-20" value="20">
                    <label for="bill-20">
                      20元=2200 玩耍币
                    </label>
                  </div>
                  <div class="radio bill-count">
                    <input type="radio" name="user-bill" id="bill-30" value="30">
                    <label for="bill-30">
                      30元=3500 玩耍币
                    </label>
                  </div>
                  <div class="radio bill-count">
                    <input type="radio" name="user-bill" id="bill-50" value="50">
                    <label for="bill-50">
                      50元=6000 玩耍币
                    </label>
                  </div>
                  <div class="radio bill-count">
                    <input type="radio" name="user-bill" id="bill-50" value="50">
                    <label for="bill-50">
                      50元=6000 玩耍币
                    </label>
                  </div>
                  <div class="radio bill-count">
                    <input type="radio" name="user-bill" id="bill-50" value="50">
                    <label for="bill-50">
                      50元=6000 玩耍币
                    </label>
                  </div>
                  <div class="radio bill-count">
                    <input type="radio" name="user-bill" id="bill-50" value="50">
                    <label for="bill-50">
                      50元=6000 玩耍币
                    </label>
                  </div>
                </div>
                <div class="clearfix"></div>
                <div class="form-group" style="text-align: center;">
                    <button type="button" class="btn btn-success btn-lg" data-toggle="modal" data-target="#pay-method">前往充值  </button>
                </div>
              </form>

            </div>
          </div>
        </div>
      </div>
      <?php include('template-parts/footer-main.php'); //引入全局底部信息 ?>
    </div>

  </div>

  <?php include('macros/modal-pay-method.php'); //引入付款方式确认模态窗口 ?>
<?php include('footer.php'); ?>