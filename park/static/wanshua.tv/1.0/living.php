<?php include('header.php'); ?>

<!-- 请将下面两个文件在对接时放入 header 相应位置 -->
<!-- 视频需要的文件 -->
<link href="/assets/js/videojs/video-js.css" rel="stylesheet">
<script src="/assets/js/videojs/ie8/videojs-ie8.min.js"></script>


    <div class="main-content">
      <div class="content page">
        <div class="content-wrapper">

          <div class="content-section video-player-banner">
            <div class="section-wrapper">
              <div class="video-avatar">
                <a href="#" title="玩家名字"><img src="assets/placeholder/avatars/5.jpg" class="img-responsive avatar" alt="玩家名字"></a>
              </div>
              <div class="video-info">
                <h1>
                  <span class="video-name">视频播放的名称</span>
                  <span class="video-game">
                    <a href="#" title="游戏名称"><i class="fa fa-gamepad"></i> 游戏名称</a>
                  </span>
                  <span class="pull-right">
                    <a href="#" title="关注 叶良辰" class="btn btn-success btn-follow btn-follow-s"><i class="fa fa-plus-circle"></i> <span class="text">关注 TA</span></a>
                  </span>
                </h1>
                <div class="video-meta">
                  <span><i class="fa fa-user"></i> <a href="#" title="玩家名字">玩家名字</a></span>
                  <span><i class="fa fa-eye"></i> 观看人数 1123</span>
                  <div class="video-action dropdown pull-right">
                    <a href="javascript:void(0);" id="dLabel" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                      手机观看
                      <span class="caret"></span>
                    </a>
                    <?php include('macros/dropdown-mobile-qrcode.php'); ?>
                  </div>

                  <div class="video-action dropdown pull-right">
                    <a href="javascript:void(0);" id="dLabel" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                      分享
                      <span class="caret"></span>
                    </a>
                    <?php include('macros/dropdown-share.php'); ?>
                  </div>

                </div>
              </div>
            </div>
          </div>

          <div class="content-section video-content">

            <div class="video-wrapper">

              <div class="video-inner">
                <video id="my-video" class="video-js" controls preload="auto" poster="assets/placeholder/videos/h8bg.png" data-setup="{}">
                  <source src="assets/placeholder/videos/h8bg.mp4" type='video/mp4'>
                  <source src="assets/placeholder/videos/h8bg.webm" type='video/webm'>
                  <p class="vjs-no-js">
                    To view this video please enable JavaScript, and consider upgrading to a web browser that
                    <a href="http://videojs.com/html5-video-support/" target="_blank">supports HTML5 video</a>
                  </p>
                </video>
              </div>

              <div class="video-actions">
                <div class="video-wallet pull-left">
                  <span class="wallet-balance">我的玩耍币: <em>12345</em></span>
                  <a href="#" class="btn btn-primary">充值</a>
                </div>
                <div class="video-gifts pull-right">
                  <!-- TODO: @Chada -->
                  <ul>
                    <li>我的贡献值: 234</li>
                    <li class="gift"><a href="javascript"><img src="/assets/images/gifts/hug.png" class="img-responsive"></a></li>
                    <li class="gift"><a href="javascript"><img src="/assets/images/gifts/papapa.png" class="img-responsive"></a></li>
                    <li class="gift"><a href="javascript"><img src="/assets/images/gifts/soap.png" class="img-responsive"></a></li>
                    <li class="gift"><a href="javascript"><img src="/assets/images/gifts/momoda.png" class="img-responsive"></a></li>
                    <li class="gift"><a href="javascript"><img src="/assets/images/gifts/jiecao.png" class="img-responsive"></a></li>
                    <li class="gift"><a href="javascript"><img src="/assets/images/gifts/knee.png" class="img-responsive"></a></li>
                </div>
              </div>

            </div>
            <!-- 请将下面这个文件在对接时放入 footer 相应位置 -->
            <!-- 视频需要的文件 -->
            <script src="/assets/js/videojs/video.min.js"></script>

          </div>

          <h2>房间简介</h2>
          <div class="content-section video-about">
            <p>我不是萌妹子，但也照样可以活的精彩。 爱我你就关注我，不爱我，也要关注我。 跪求礼物思密达~ 四点开始直播，每个半点露脸！ 自由之战不败id：26641383124 房间开黑密码: 9876 主播qq群： 208358353</p>
          </div>


          <h2>评论</h2>
          <div class="content-section comments">
            <?php include('template-parts/comments.php'); ?>
          </div>

          <?php include('template-parts/content-related.php'); //引入相关视频列表 ?>

          <?php include('template-parts/footer-main.php'); //引入全局底部信息 ?>

        </div>
      </div>

      <!-- 聊天模块 TODO: @Chada -->
      <?php include('template-parts/sidebar-living.php'); // 引入侧边栏聊天与观看者名单 ?>

    </div>

<?php include('footer.php'); ?>