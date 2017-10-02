<?php include('header_m.php'); ?>
  <div class="living-wrapper">
    <div id="living-video" class="living">
      <!-- 请将下面两个文件在对接时放入 header 相应位置 -->
      <!-- 视频需要的文件 -->
      <link href="/assets/js/videojs/video-js.css" rel="stylesheet">
      <script src="/assets/js/videojs/ie8/videojs-ie8.min.js"></script>

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
      </div>

      <!-- 请将下面这个文件在对接时放入 footer 相应位置 -->
      <!-- 视频需要的文件 -->
      <script src="/assets/js/videojs/video.min.js"></script>
    </div>

    <ul id="living-nav" class="nav nav-tabs living-tabs" role="tablist">
      <li role="presentation" class="active"><a href="#living-about" aria-controls="living-about" role="tab" data-toggle="tab">简介</a></li>
      <li role="presentation"><a href="#living-chat" aria-controls="living-chat" role="tab" data-toggle="tab">聊天</a></li>
      <li role="presentation"><a href="#living-board" aria-controls="living-board" role="tab" data-toggle="tab">土豪榜</a></li>
      <li role="presentation"><a href="#living-related" aria-controls="living-related" role="tab" data-toggle="tab">Ta 的视频</a></li>
    </ul>

    <div id="living-content" class="living-content tab-content">
      <!-- 房间简介 -->
      <div role="tabpanel" class="tab-pane page-section active" id="living-about">
        <div class="video-player-banner">
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
              </h1>
              <div class="video-meta">
                <span><i class="fa fa-user"></i> <a href="#" title="玩家名字">玩家名字</a></span>
                <span><i class="fa fa-eye"></i> 观看人数 1123</span>

                <div class="video-action dropdown pull-right">
                  <a href="javascript:void(0);" id="dLabel" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    <i class="fa fa-share"></i> 分享
                    <span class="caret"></span>
                  </a>
                  <?php include('macros/dropdown-share.php'); ?>
                </div>

              </div>

            </div>
          </div>
        </div>
        <h3>房间简介</h3>
        <div class="section-content video-about">
          <p>我不是萌妹子，但也照样可以活的精彩。 爱我你就关注我，不爱我，也要关注我。 跪求礼物思密达~ 四点开始直播，每个半点露脸！ 自由之战不败id：26641383124 房间开黑密码: 9876 主播qq群： 208358353</p>
        </div>
      </div>

      <!-- 聊天 -->
      <div role="tabpanel" class="tab-pane page-section chat-section" id="living-chat">
        <div class="chat-list-wrapper">
          <div id="chatWindow" class="chat-list">
            <div class="bubble"><span class="sender">张三</span>: <span class="msg">msg<img src="assets/images/gifts/hug.png" width="60" height="60"></span></div>
            <div class="bubble"><span class="sender">李四</span>: <span class="msg">long message</span></div>
            <div class="bubble"><span class="sender">张三</span>: <span class="msg">ultra long message which can wrap at eighty percent </span></div>
            <div class="bubble player"><span class="sender">王五</span>: <span class="msg">lorem ipsum</span></div> <!-- 主播发送的消息 -->
            <div class="bubble"><span class="sender">张三</span>: <span class="msg">very long message</span></div>
            <div class="bubble mine"><span class="sender">我</span>: <span class="msg">one more message</span></div> <!-- 当前用户发送的消息 -->
            <div class="bubble"><span class="sender">张三</span>: <span class="msg">lorem ipsum</span></div>
            <div class="bubble"><span class="sender">长长的用户名</span>: <span class="msg">another message</span></div>
            <div class="bubble"><span class="sender">张三</span>: <span class="msg">lorem ipsum</span></div>
            <div class="bubble"><span class="sender">张三</span>: <span class="msg">yet another message</span></div>
            <div class="bubble"><span class="sender">张三</span>: <span class="msg">lorem ipsum</span></div>
            <div class="bubble"><span class="sender">张三</span>: <span class="msg">lorem ipsum</span></div>
            <div class="bubble"><span class="sender">张三</span>: <span class="msg">very long message</span></div>
            <div class="bubble"><span class="sender">张三</span>: <span class="msg">one more message</span></div>
            <div class="bubble"><span class="sender">张三</span>: <span class="msg">lorem ipsum</span></div>
            <div class="bubble"><span class="sender">张三</span>: <span class="msg">another message</span></div>
            <div class="bubble"><span class="sender">张三</span>: <span class="msg">lorem ipsum</span></div>
            <div class="bubble"><span class="sender">张三</span>: <span class="msg">yet another message</span></div>
            <div class="bubble"><span class="sender">张三</span>: <span class="msg">lorem ipsum</span></div>
            <div id="nothing"></div> <!-- 在demo中，这一行不能删除，是用来插入新的聊天消息时判断位置的 -->
          </div>
          <div id="inputWindow" class="chat-input-field">
            <div class="error-note"><span>发送消息太频繁啦～</span></div>
            <input id="inp" type="text" placeholder="来一发弹幕...">
            <button id="btn" type="button"><i class="fa fa-rocket"></i></button>
          </div>
        </div>
      </div>

      <!-- 土豪榜 -->
      <div role="tabpanel" class="tab-pane page-section" id="living-board">
        <ul class="board-list">
          <li>
            <span class="player-rate">1</span>
            <span class="player-karma">14级</span>
            <span class="player-info">排行榜用户1</span>
          </li>
          <li>
            <span class="player-rate">2</span>
            <span class="player-karma">14级</span>
            <span class="player-info">排行榜用户1</span>
          </li>
          <li>
            <span class="player-rate">3</span>
            <span class="player-karma">14级</span>
            <span class="player-info">排行榜用户1</span>
          </li>
          <li>
            <span class="player-rate">4</span>
            <span class="player-karma">14级</span>
            <span class="player-info">排行榜用户1</span>
          </li>
          <li>
            <span class="player-rate">5</span>
            <span class="player-karma">14级</span>
            <span class="player-info">排行榜用户1</span>
          </li>
        </ul>
      </div>

      <!-- 相关视频 -->
      <div role="tabpanel" class="tab-pane page-section" id="living-related">
        <div class="section-content">
          <ul id="home-videos" class="video-list">
            <li class="video">
              <div class="video-wrapper">
                <div class="video-cover" style="background-image: url(assets/placeholder/videos/1.jpg);">
                  <a href="#" class="video-link" title="直播名称">直播名称</a>
                  <div class="video-meta">
                    <h4><a href="#">直播名称啊直播名称</a></h4>
                    <span class="video-viewers"><i class="fa fa-eye"></i> 2341</span>
                  </div>
                  <span class="live-sign">LIVE</span>
                </div>
                <div class="video-player">
                  <img src="assets/placeholder/avatars/11.jpg" class="avatar img-responsive" alt="玩家名字">
                  <span class="player-name">张三李四什么的</span>
                </div>
              </div>
            </li>

            <li class="video">
              <div class="video-wrapper">
                <div class="video-cover" style="background-image: url(assets/placeholder/videos/2.jpg);">
                  <a href="#" class="video-link" title="直播名称">直播名称</a>
                  <div class="video-meta">
                    <h4><a href="#">直播名称啊直播名称</a></h4>
                    <span class="video-viewers"><i class="fa fa-eye"></i> 2341</span>
                  </div>
                </div>
                <div class="video-player">
                  <img src="assets/placeholder/avatars/13.jpg" class="avatar img-responsive" alt="玩家名字">
                  <span class="player-name">张三李四什么的</span>
                </div>
              </div>
            </li>

            <li class="video">
              <div class="video-wrapper">
                <div class="video-cover" style="background-image: url(assets/placeholder/videos/3.jpg);">
                  <a href="#" class="video-link" title="直播名称">直播名称</a>
                  <div class="video-meta">
                    <h4><a href="#">直播名称啊直播名称</a></h4>
                    <span class="video-viewers"><i class="fa fa-eye"></i> 2341</span>
                  </div>
                </div>
                <div class="video-player">
                  <img src="assets/placeholder/avatars/14.jpg" class="avatar img-responsive" alt="玩家名字">
                  <span class="player-name">张三李四什么的</span>
                </div>
              </div>
            </li>

            <li class="video">
              <div class="video-wrapper">
                <div class="video-cover" style="background-image: url(assets/placeholder/videos/4.jpg);">
                  <a href="#" class="video-link" title="直播名称">直播名称</a>
                  <div class="video-meta">
                    <h4><a href="#">直播名称啊直播名称</a></h4>
                    <span class="video-viewers"><i class="fa fa-eye"></i> 2341</span>
                  </div>
                </div>
                <div class="video-player">
                  <img src="assets/placeholder/avatars/1.jpg" class="avatar img-responsive" alt="玩家名字">
                  <span class="player-name">张三李四什么的</span>
                </div>
              </div>
            </li>

            <li class="video">
              <div class="video-wrapper">
                <div class="video-cover" style="background-image: url(assets/placeholder/videos/5.jpg);">
                  <a href="#" class="video-link" title="直播名称">直播名称</a>
                  <div class="video-meta">
                    <h4><a href="#">直播名称啊直播名称</a></h4>
                    <span class="video-viewers"><i class="fa fa-eye"></i> 2341</span>
                  </div>
                </div>
                <div class="video-player">
                  <img src="assets/placeholder/avatars/2.jpg" class="avatar img-responsive" alt="玩家名字">
                  <span class="player-name">张三李四什么的</span>
                </div>
              </div>
            </li>

            <li class="video">
              <div class="video-wrapper">
                <div class="video-cover" style="background-image: url(assets/placeholder/videos/1.jpg);">
                  <a href="#" class="video-link" title="直播名称">直播名称</a>
                  <div class="video-meta">
                    <h4><a href="#">直播名称啊直播名称</a></h4>
                    <span class="video-viewers"><i class="fa fa-eye"></i> 2341</span>
                  </div>
                </div>
                <div class="video-player">
                  <img src="assets/placeholder/avatars/11.jpg" class="avatar img-responsive" alt="玩家名字">
                  <span class="player-name">张三李四什么的</span>
                </div>
              </div>
            </li>

            <li class="video">
              <div class="video-wrapper">
                <div class="video-cover" style="background-image: url(assets/placeholder/videos/1.jpg);">
                  <a href="#" class="video-link" title="直播名称">直播名称</a>
                  <div class="video-meta">
                    <h4><a href="#">直播名称啊直播名称</a></h4>
                    <span class="video-viewers"><i class="fa fa-eye"></i> 2341</span>
                  </div>
                </div>
                <div class="video-player">
                  <img src="assets/placeholder/avatars/11.jpg" class="avatar img-responsive" alt="玩家名字">
                  <span class="player-name">张三李四什么的</span>
                </div>
              </div>
            </li>

            <li class="video">
              <div class="video-wrapper">
                <div class="video-cover" style="background-image: url(assets/placeholder/videos/1.jpg);">
                  <a href="#" class="video-link" title="直播名称">直播名称</a>
                  <div class="video-meta">
                    <h4><a href="#">直播名称啊直播名称</a></h4>
                    <span class="video-viewers"><i class="fa fa-eye"></i> 2341</span>
                  </div>
                </div>
                <div class="video-player">
                  <img src="assets/placeholder/avatars/11.jpg" class="avatar img-responsive" alt="玩家名字">
                  <span class="player-name">张三李四什么的</span>
                </div>
              </div>
            </li>

            <li class="video">
              <div class="video-wrapper">
                <div class="video-cover" style="background-image: url(assets/placeholder/videos/1.jpg);">
                  <a href="#" class="video-link" title="直播名称">直播名称</a>
                  <div class="video-meta">
                    <h4><a href="#">直播名称啊直播名称</a></h4>
                    <span class="video-viewers"><i class="fa fa-eye"></i> 2341</span>
                  </div>
                </div>
                <div class="video-player">
                  <img src="assets/placeholder/avatars/11.jpg" class="avatar img-responsive" alt="玩家名字">
                  <span class="player-name">张三李四什么的</span>
                </div>
              </div>
            </li>

            <li class="video">
              <div class="video-wrapper">
                <div class="video-cover" style="background-image: url(assets/placeholder/videos/1.jpg);">
                  <a href="#" class="video-link" title="直播名称">直播名称</a>
                  <div class="video-meta">
                    <h4><a href="#">直播名称啊直播名称</a></h4>
                    <span class="video-viewers"><i class="fa fa-eye"></i> 2341</span>
                  </div>
                </div>
                <div class="video-player">
                  <img src="assets/placeholder/avatars/11.jpg" class="avatar img-responsive" alt="玩家名字">
                  <span class="player-name">张三李四什么的</span>
                </div>
              </div>
            </li>


          </ul>
        </div>
      </div>
    </div>
  </div>
  <?php include('macros/download-banner.php'); ?>

<?php include('footer_m.php'); ?>