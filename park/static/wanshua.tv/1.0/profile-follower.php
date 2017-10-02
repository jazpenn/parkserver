<?php include('header.php'); ?>
  <div class="main-content" id="index-content">
      <div class="content page profile-page">
        <div class="content-wrapper">
          <?php include('template-parts/content-profile.php'); //引入用户信息 ?>

          <h2>Ta 的粉丝 (116)</h2>
          <div class="content-inner video-list">

            <?php include('template-parts/profile-userlist.php'); //引入用户列表 ?>

            <!-- 如果没有关注任何用户 -->
            <?php //include('template-parts/profile-follower-none.php'); //没有视频 ?>

          </div>

          <div class="content-load-more">

          </div>

        </div>
      </div>

    </div>

<?php include('footer.php'); ?>