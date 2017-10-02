<?php include('header.php'); ?>
  <div class="main-content" id="index-content">
      <div class="content page profile-page">
        <div class="content-wrapper">
          <?php include('template-parts/content-profile.php'); //引入用户信息 ?>

          <!-- 如果有视频 -->
          <?php include('template-parts/content-related.php'); //引入相关视频列表 ?>

          <!-- 如果没有视频 -->
          <?php //include('template-parts/profile-video-none.php'); //没有视频 ?>
        </div>
      </div>

    </div>

<?php include('footer.php'); ?>