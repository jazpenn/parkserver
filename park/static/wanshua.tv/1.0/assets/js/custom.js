  // jQuery $ conflict init
  var $ = jQuery.noConflict();

  $(document).ready(function () {

    $('a.modal-btn').on('click', function() {
        whichtab = $(this).data('opentab');
        $('#modal-login').modal('show');
        $('.nav-tabs li:eq('+whichtab+') a').tab('show');
    });

    //enable tooltip
    // $('[data-toggle="tooltip"]').tooltip();

    var windowWidth = $(window).width();
    var windowHeight = $(window).height();
    var headerHeight = $('.navbar').height();
    // 首页首屏
    $('.hero-item').css({ // 临时控制首页首屏样式
      'height' : windowWidth * 6 / 16 + 'px',
    });

    var heroHeight = $('.hero-item').height();
    var heroContentHeight = $('.hero-item-content').height();
    if (heroHeight > heroContentHeight) {
      $('.hero-item-content').css({
        'padding-top' : (heroHeight - heroContentHeight) / 2 + 'px',
      });
    }

    $('#main-sidebar').css({
      'height' : windowHeight - headerHeight + 'px',
    });

    $('#video-sidebar').css({
      'height' : windowHeight - headerHeight + 'px',
    });

    //Home Sticky Sidebar
    var didScroll;
    var lastScrollTop = 0;
    var delta = 5;
    $('.wrapper').scroll(function(event){
        didScroll = true;
        // console.log('I am scrolling');
        // console.log('sidebar top:' + sidebarTop);

    });

    setInterval(function() {
        if (didScroll) {
            hasScrolled();
            didScroll = false;
        }
    }, 250);

    function hasScrolled() {
        var st = $('.wrapper').scrollTop();
        var sh = $('.index-hero').height() - $('.navbar').height();
        var sidebarTop = $("#main-sidebar").offset().top + sh;


        // If they scrolled down and are past the navbar, add class .nav-up.
        // This is necessary so you never see what is "behind" the navbar.
        if (st > lastScrollTop && st > sidebarTop){
            $("#main-sidebar").addClass('is-sticky');
        } else {
            $("#main-sidebar").removeClass('is-sticky');
            lastScrollTop = st;
        }
    };

    //Other Sidebar Height
    $('#aside-container').css({
        'height' : windowHeight - headerHeight - $('#aside-header').height(),
    });

    //Video Reset
    var videoWidth = $('.my-video-dimensions').width();
    $('.my-video-dimensions').css({
        'height' : videoWidth * 9 / 16 + 'px',
    });
  })
