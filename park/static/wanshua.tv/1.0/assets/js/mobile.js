$("#home-featured").owlCarousel({
  loop: true,
  navigation : false, // Show next and prev buttons
  slideSpeed : 300,
  paginationSpeed : 400,
  items : 1,
  itemsDesktop : false,
  itemsDesktopSmall : false,
  itemsTablet: true,
  itemsMobile : true,
  autoplay: 2000
});

$("#home-player").owlCarousel({
  loop: true,
  navigation : false, // Show next and prev buttons
  slideSpeed : 300,
  paginationSpeed : 400,
  items : 5,
  itemsDesktop : false,
  itemsDesktopSmall : false,
  itemsTablet: true,
  itemsMobile : true,
});

$('#download-close').click(function(){
  $('#download-banner').remove();
});

//Video Reset 如果不需要刻意去除
var windowWidth = $(window).width();
$('#my-video').css({
  'width' : windowWidth,
  'height' : windowWidth * 3 / 4 + 'px',
});

$('#living-content').css({
  'height' : $(window).height() -  $('#m-header').height() - $('#living-video').height() - $('#living-nav').height(),
});