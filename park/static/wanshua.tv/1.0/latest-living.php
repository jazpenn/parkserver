<?php include('header.php'); ?>
    <div class="main-content" id="index-content">
      <div class="content page">
        <div class="content-wrapper">

          <?php include('template-parts/content-home.php'); //引入首页视频列表 ?>

          <?php include('template-parts/footer-main.php'); //引入全局底部信息 ?>

        </div>
      </div>

      <?php include('template-parts/sidebar-player.php'); // 引入侧边栏推荐主播 ?>

    </div>

<?php include('footer.php'); ?>