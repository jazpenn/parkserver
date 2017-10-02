(function($){

    $.fn.outerFind = function(selector){
        return this.find(selector).addBack(selector);
    };

    (function(){
        
        var scrollbarWidth = 0, originalMargin, touchHandler = function(event){
            event.preventDefault();
        };

        function getScrollbarWidth(){
            if (scrollbarWidth) return scrollbarWidth;
            var scrollDiv = document.createElement('div');
            $.each({
                top : '-9999px',
                width  : '50px',
                height : '50px',
                overflow : 'scroll', 
                position : 'absolute'
            }, function(property, value){
                scrollDiv.style[property] = value;
            });
            $('body').append(scrollDiv);
            scrollbarWidth = scrollDiv.offsetWidth - scrollDiv.clientWidth;
            $('body')[0].removeChild(scrollDiv);
            return scrollbarWidth;
        }

        $.fn.fullscreen = function(yes){
            if (yes){
                originalMargin = document.body.parentNode.style.marginRight || '';
                var fullWindowWidth = window.innerWidth;
                if (!fullWindowWidth){
                    var documentElementRect = document.documentElement.getBoundingClientRect();
                    fullWindowWidth = documentElementRect.right - Math.abs(documentElementRect.left);
                }
                if (fullWindowWidth > document.body.clientWidth){
                    $('html').css({
                        'margin-right' : parseInt(($('html').css('margin-right') || 0), 10) + getScrollbarWidth(),
                        'overflow' : 'hidden'
                    }).addClass('mbr-hidden-scrollbar');
                }
                this.addClass('mbr-fullscreen');
                $(window).bind('touchmove', touchHandler).resize();
            } else {
                this.removeClass('mbr-fullscreen').css('height', '');
                $('html').css({
                    'margin-right' : originalMargin,
                    'overflow' : ''
                }).removeClass('mbr-hidden-scrollbar');
                $(window).unbind('touchmove', touchHandler);
            }
            return this;
        };

    })();

    $.isMobile = function(type){
        var reg = [];
        var any = {
            blackberry : 'BlackBerry',
            android : 'Android',
            windows : 'IEMobile',
            opera : 'Opera Mini',
            ios : 'iPhone|iPad|iPod'
        };
        type = 'undefined' == $.type(type) ? '*' : type.toLowerCase();
        if ('*' == type) reg = $.map(any, function(v){ return v; });
        else if (type in any) reg.push(any[type]);
        return !!(reg.length && navigator.userAgent.match(new RegExp(reg.join('|'), 'i')));
    };

    $(function(){

        $('html').addClass($.isMobile() ? 'mobile' : 'desktop');

        // .mbr-fullscreen
        (function(width, height){
            var deviceSize = [width, width];
            deviceSize[height > width ? 0 : 1] = height;
            $(window).resize(function(){
                var windowHeight = $(window).height();
                // simple fix for Chrome's scrolling
                if ($.isMobile() && navigator.userAgent.match(/Chrome/i) && $.inArray(windowHeight, deviceSize) < 0)
                    windowHeight = deviceSize[ $(window).width() > windowHeight ? 1 : 0 ];
                $('.mbr-fullscreen').each(function(){
                    var reserved = 0;
                    var prev = $(this).prev();
                    if (prev.hasClass('static') && prev.outerHeight() < windowHeight / 3)
                        reserved += prev.outerHeight();
                    $(this).css('height', (windowHeight - reserved) + 'px');
                });
            });
        })($(window).width(), $(window).height());
        $(document).on('add.cards', function(event){
            if ($('html').hasClass('mbr-site-loaded') && $(event.target).outerFind('.mbr-fullscreen').length)
                $(window).resize();
        });

        // .mbr-parallax-background
        $(document).on('add.cards', function(event){
            $(event.target).outerFind('.mbr-parallax-background:not(.mbr-added)').each(function(){
                $(this).addClass('mbr-added');
                if (!$.isMobile()) $(this).parallax('50%', 0.3, true);
            });
        });

        // .mbr-social-likes
        $(document).on('add.cards', function(event){
            $(event.target).outerFind('.mbr-social-likes:not(.mbr-added)').on('counter.social-likes', function(event, service, counter){
                if (counter > 999) $('.social-likes__counter', event.target).html(Math.floor(counter / 1000) + 'k');
            }).socialLikes({initHtml : false});
        });

        // .mbr-nav-collapse, .mbr-nav-toggle
        $(window).resize(function(){
            if ($(window).width() > 780){
                $('.mbr-nav-collapse:not(.collapsed)').removeClass('nav-collapsed mbr-nav-visible')
                    .find('.mbr-nav-toggle.opened').click();
            } else {
                $('.mbr-nav-collapse').addClass('nav-collapsed')
                    .find('.mbr-nav-toggle').show();
            }
        }).keydown(function(event){
            if (27 == event.which) // ESC
                $('.mbr-nav-toggle.opened').click();
        });
        $(document).on('add.cards', function(event){
            $('.mbr-nav-toggle:not(.mbr-added)', event.target).addClass('mbr-added').click(function(){
                var parent = $(this).parents('[class|="menu"]');
                var open = !$(this).hasClass('opened');
                $('nav', parent).fullscreen(open);
                $(this)[ (open ? 'add' : 'remove') + 'Class' ]('opened');
                parent[ (open ? 'add' : 'remove') + 'Class' ]('mbr-nav-visible')
                    .css('top', open ? $(window).scrollTop() : '');
            }).parents('[class|="menu"]').find('nav a').click(function(){
                $('.mbr-nav-toggle.opened').click();
            });
        });

        // .mbr-fixed-top
        var fixedTopTimeout, scrollTimeout, prevScrollTop = 0, fixedTop = null, isDesktop = !$.isMobile();
        $(window).scroll(function(){
            if (scrollTimeout) clearTimeout(scrollTimeout);
            var scrollTop = $(window).scrollTop();
            var scrollUp  = scrollTop <= prevScrollTop || isDesktop;
            prevScrollTop = scrollTop;
            if (fixedTop){
                var fixed = scrollTop > fixedTop.breakPoint;
                if (scrollUp){
                    if (fixed != fixedTop.fixed){
                        if (isDesktop){
                            fixedTop.fixed = fixed;
                            $(fixedTop.elm).toggleClass('is-fixed');
                        } else {
                            scrollTimeout = setTimeout(function(){
                                fixedTop.fixed = fixed;
                                $(fixedTop.elm).toggleClass('is-fixed');
                            }, 40);
                        }
                    }
                } else {
                    fixedTop.fixed = false;
                    $(fixedTop.elm).removeClass('is-fixed');
                }
            }
        });
        $(document).on('add.cards remove.cards', function(event){
            if (fixedTopTimeout) clearTimeout(fixedTopTimeout);
            fixedTopTimeout = setTimeout(function(){
                if (fixedTop){
                    fixedTop.fixed = false;
                    $(fixedTop.elm).removeClass('is-fixed');
                }
                $('.mbr-fixed-top:first').each(function(){
                    fixedTop = {
                        breakPoint : $(this).offset().top + $(this).height() * 3,
                        fixed : false,
                        elm : this
                    };
                    $(window).scroll();
                });
            }, 650);
        });

        // embedded videos
        $(window).resize(function(){
            $('.row iframe[src*="youtube.com"], .row iframe[src*="player.vimeo.com"]').each(function(){
                $(this).height(
                    $(this).width() *
                    parseInt($(this).attr('height') || 315) /
                    parseInt($(this).attr('width') || 560)
                );
            });
        });
        $(document).on('add.cards', function(event){
            if ($('html').hasClass('mbr-site-loaded') && $(event.target).outerFind('iframe').length)
                $(window).resize();
        });

        // background video
        var updateBgImgPosition = function(img){
            var win = {
                width : img.parent().outerWidth(),
                height : img.parent().outerHeight()
            };
            var ratio = '16/9';
            var margin = 24;
            var overprint = 100;
            var css = {display : 'block'};
            css.width = win.width + ((win.width * margin) / 100);
            css.height = ratio == '16/9' ? Math.ceil((9 * win.width) / 16) : Math.ceil((3 * win.width) / 4);
            css.marginTop = -((css.height - win.height) / 2);
            css.marginLeft = -((win.width * (margin / 2)) / 100);
            if (css.height < win.height){
                css.height = win.height + ((win.height * margin) / 100);
                css.width = ratio == '16/9' ? Math.floor((16 * win.height) / 9) : Math.floor((4 * win.height) / 3);
                css.marginTop = -((win.height * (margin / 2)) / 100);
                css.marginLeft = -((css.width - win.width) / 2);
            }
            css.width += overprint;
            css.height += overprint;
            css.marginTop -= overprint / 2;
            css.marginLeft -= overprint / 2;
            img.css(css);
        };
        $(window).resize(function(){
            $('.mbr-background-video-preview img').each(function(){
                updateBgImgPosition($(this));
            });
        });
        $(document).on('add.cards', function(event){
            $(event.target).outerFind('[data-bg-video]').each(function(){
                var result, videoURL = $(this).data('bg-video'), patterns = [
                    /\?v=([^&]+)/,
                    /(?:embed|\.be)\/([a-z0-9]+)/i,
                    /^([a-z0-9]+)$/i
                ];
                for (var i = 0; i < patterns.length; i++){
                    if (result = patterns[i].exec(videoURL)){
                        $('.container:eq(0)', this).before('<div class="mbr-background-video-preview"><img style="display:none;" src="//img.youtube.com/vi/' + result[1] + '/maxresdefault.jpg"></div>');
                        if (!$.isMobile()){
                            var params = eval('(' + ($(this).data('bg-video-params') || '{}') + ')');
                            $('.container:eq(0)', this).before('<div class="mbr-background-video"></div>').prev()
                                .YTPlayer($.extend({
                                    videoURL : result[1],
                                    containment : 'self',
                                    showControls : false,
                                    mute : true
                                }, params));
                        }
                        break;
                    }
                }
            });
        });

        // init
        $('body > *:not(style, script)').trigger('add.cards');
        $('html').addClass('mbr-site-loaded');
        $(window).resize().scroll();

        // scrolling effects
        $('[data-effect]').addClass('mbr-transparent').viewportChecker({
            offset: '10%',
            callbackFunction: function(elem, action){
                var data = ($(elem).data('effect') || 'fadeIn').split(/\s+/g);
                if (data.length < 2) data.push('0');
                setTimeout(function(){
                    elem.removeClass('mbr-transparent')
                        .addClass('animated ' + data[0]);
                }, parseInt(data[1]));
            }
        });

    });

})(jQuery);