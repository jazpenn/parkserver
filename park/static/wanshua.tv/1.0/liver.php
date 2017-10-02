<?php include('header.php'); ?>
  <div class="main-content" id="index-content">
    <div class="content page profile-page">
      <div class="content-wrapper">
        <div class="row">
          <div class="col-lg-4 col-md-4 col-sm-12 col-xs-12 settings-sidebar">
            <div class="sidebar-wrapper">
              <h2><i class="fa fa-microphone"></i> 主播中心</h2>
              <ul class="">
                <li class="active"><a href="liver.php">概览</a></li>
                <li><a href="liver-earnings.php">我的收入</a></li>
                <li><a href="liver-balance.php">我的余额</a></li>
                <li><a href="liver-board.php">我的排名</a></li>
              </ul>
            </div>
          </div>


          <div class="col-lg-8 col-md-8 col-sm-12 col-xs-12 settings-content">
            <div class="settings-content-wrapper">
              <h3>主播中心</h3>
              <div class="settings-section">
                <div class="settings-section-wrapper row">
                  <div class="col-lg-4 settings-grid">
                    <div class="grid-wrapper">
                      <h4>我的余额</h4>
                      <div class="grid-data">¥300.00</div>
                      <div class="grid-link"><small><a href="liver-balance.php" class="grid-jump">查看详情 &raquo;</a></small></div>
                    </div>
                  </div>
                  <div class="col-lg-4 settings-grid">
                    <div class="grid-wrapper">
                      <h4>我的玩耍币</h4>
                      <div class="grid-data">52357</div>
                      <div class="grid-link"><small><a href="liver-earnings.php" class="grid-jump">查看详情 &raquo;</a></small></div>
                    </div>
                  </div>
                  <div class="col-lg-4 settings-grid">
                    <div class="grid-wrapper">
                      <h4>我的排名</h4>
                      <div class="grid-data">23</div>
                      <div class="grid-link"><small><a href="liver-board.php" class="grid-jump">查看详情 &raquo;</a></small></div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="settings-section">
                <h4 class="section-title">主播规则：</h4>
                <ul>
                  <li>第一条规则</li>
                  <li>第二条规则</li>
                  <li>第三条规则</li>
                  <li>第四条规则</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
      <?php include('template-parts/footer-main.php'); //引入全局底部信息 ?>
    </div>

  </div>

  <?php include('macros/modal-pay-method.php'); //引入付款方式确认模态窗口 ?>
<?php include('footer.php'); ?>