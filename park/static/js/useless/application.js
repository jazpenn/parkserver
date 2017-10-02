/* 
* @Author: J.Y Han
* @Date:   2013-11-02 12:44:25
* @Email:  jiyun@han.im
* @Last modified by:   hanjiyun
* @Last Modified time: 2013-11-30 17:21:48
*/

$(function(){

    var $modalSYS = $('#sys-modal');

    // tooltip
    $('.tooltips').tooltip();

    // 导航下拉
    $('#header .navbar-nav-user').hover(function(){
        $(this).addClass('active');
        $(this).find('.dropdown').show();
    },function(){
        $(this).removeClass('active');
        $(this).find('.dropdown').hide();
    })

    // 导航搜索框
    $('#sub-header .navbar-form input').focus(function(){
        $(this).attr('placeholder', '搜索 手游、视频、攻略')
        $(this).parents('.navbar-form').eq(0).addClass('search_opend')
    }).blur(function(){
        $(this).attr('placeholder', '搜索')
        $(this).parents('.navbar-form').eq(0).removeClass('search_opend')
    })

    // 回应 删除 举报 显示隐藏
    $('.review_reply li').hover(function(){
        $(this).find('.g_r_ctl').css({
            'visibility':'visible'
        })
    },function(){
        $(this).find('.g_r_ctl').css({
            'visibility':'hidden'
        })
    })

    // 顶
    $('.v_up').click(function(){

        if($(this).hasClass('active')){
            return;
            // alert('已经顶过了')
        }else{
            var t = $(this),
                a = t.find('a'),
                film_id = parseInt(a.data('filmid')),
                action = 'vote';

            var data =  { film_id : film_id, action : action };
            
            t.addClass('active');
            $('.v_down').removeClass('active').find('a').html('<i class="icon-thumbs-down"></i>');

            $.ajax({
                url : '/api/film/vote',
                type : 'POST',
                contentType : 'application/json;charset=UTF-8',
                data : JSON.stringify(data),
                dataType : "json",
                beforeSend : function(XMLHttpRequest){
                    a.html('<i class="icon-thumbs-up"></i> 稍等...')
                 },
                success:function(mes){
                    if (mes.ok == 'ok'){
                        a.html('<i class="icon-thumbs-up"></i> 已顶');
                    }
                },
                complete:function(XMLHttpRequest,textStatus){
                    //
                },
                error:function(XMLHttpRequest, textStatus, errorThrown){
                    t.removeClass('active').find('a').html('<i class="icon-thumbs-up"></i> 顶');
                    var m = JSON.parse(XMLHttpRequest.responseText)
                    if(m.errnum == 300){
                        var location = window.location;
                        m.errmsg =  '还没有登录，请先 <a class="btn btn-success" href="/login?next='+ location +'">登录</a>';
                    }
                    $modalSYS.modal().find('.modal-body').html(m.errmsg)
                }
            })
        }
    })

    // 踩
    $('.v_down').click(function(){

        if($(this).hasClass('active')){
            return;
            // alert('已经踩过了')
        }else{
            var t = $(this),
                a = t.find('a'),
                film_id = parseInt(a.data('filmid')),
                action = 'unvote';

            var data =  { film_id : film_id, action : action };

            t.addClass('active');
            $('.v_up').removeClass('active').find('a').html('<i class="icon-thumbs-up"></i> 顶');

            $.ajax({
                url : '/api/film/vote',
                type : 'POST',
                contentType : 'application/json;charset=UTF-8',
                data : JSON.stringify(data),
                dataType : "json",
                beforeSend : function(XMLHttpRequest){
                    a.html('<i class="icon-thumbs-down"></i> 稍等...')
                 },
                success:function(mes){
                    if (mes.ok == 'ok'){
                        a.html('<i class="icon-thumbs-down"></i> 已踩');
                    }
                },
                complete:function(XMLHttpRequest,textStatus){
                    //
                },
                error:function(XMLHttpRequest, textStatus, errorThrown){
                    t.removeClass('active').find('a').html('<i class="icon-thumbs-down"></i>');
                    var m = JSON.parse(XMLHttpRequest.responseText)
                    if(m.errnum == 300){
                        var location = window.location;
                        m.errmsg =  '还没有登录，请先 <a class="btn btn-success" href="/login?next='+ location +'">登录</a>';
                    }
                    $modalSYS.modal().find('.modal-body').html(m.errmsg)
                }
            })
        }
    })

    // 喜欢&取消喜欢 收藏/取消收藏
    
    $('.btn-like').click(function(){

        var t = $(this),
            content_id = t.data('content_id'),
            content_type = t.data('content_type'),
            count = parseInt(t.find('em').text());

        //error vaild
        if (count < 0) return;
        if (t.hasClass('active') && count == 0) return;

        if(t.hasClass('active')){
            var action = 'unlike';
            count = count - 1;
        } else {
            var action = 'like';
            count = count + 1;
        }

        var data =  { content_id : content_id, content_type : content_type, action : action };

        $.ajax({
            url : '/api/content/like',
            type : 'POST',
            contentType : 'application/json;charset=UTF-8',
            data : JSON.stringify(data),
            dataType : "json",
            beforeSend : function(XMLHttpRequest){
                 $('body').modalmanager('loading');

             },
            success:function(mes){
                $('body').modalmanager('removeLoading').removeClass('modal-open page-overflow');
                if (mes.ok == 'ok'){
                    
                    if(t.hasClass('active')){
                        t.removeClass('active');
                    } else {
                        t.addClass('active');
                    }
                    t.find('em').html(count); //rewrite count
                }
            },
            complete:function(XMLHttpRequest,textStatus){
                // $('body').modalmanager('removeLoading').removeClass('modal-open page-overflow');
            },
            error:function(XMLHttpRequest, textStatus, errorThrown){
                $('body').modalmanager('removeLoading').removeClass('modal-open page-overflow');
                var m = JSON.parse(XMLHttpRequest.responseText)
                if(m.errnum == 300){
                    var location = window.location;
                    m.errmsg =  '还没有登录，请先 <a class="btn btn-success" href="/login?next='+ location +'">登录</a>';
                }
                $modalSYS.modal().find('.modal-body').html(m.errmsg)
            }
        })
    })

    // 关注
    $('#btn-follow').click(function(){
        var t = $(this);
        var user_id = t.data('userid');
        var data =  { user_id : user_id, action : 'follow' };

        $.ajax({
            url : '/api/user/follow',
            type : 'POST',
            contentType : 'application/json;charset=UTF-8',
            data : JSON.stringify(data),
            dataType : "json",
            beforeSend : function(XMLHttpRequest){
                 $('body').modalmanager('loading');
             },
            success:function(mes){
                if (mes.ok == 'ok'){
                    t.addClass('hide');
                    t.next('.btn-group').removeClass('hide');
                    location.reload();

                }
            },
            complete:function(XMLHttpRequest,textStatus){
                // $('body').modalmanager('removeLoading').removeClass('modal-open page-overflow');
            },
            error:function(XMLHttpRequest, textStatus, errorThrown){
                $('body').modalmanager('removeLoading').removeClass('modal-open page-overflow');
                var m = JSON.parse(XMLHttpRequest.responseText)
                if(m.errnum == 300){
                    var location = window.location;
                    m.errmsg =  '还没有登录，请先 <a class="btn btn-success" href="/login?next='+ location +'">登录</a>';
                }
                $modalSYS.modal().find('.modal-body').html(m.errmsg)
            }
        })
     })


    // 取消关注
    $('#btn-nofollow').click(function(){

        var t = $(this);
        var user_id = t.data('userid');
        var data =  { user_id : user_id, action : 'unfollow' };

        $.ajax({
            url : '/api/user/follow',
            type : 'POST',
            contentType : 'application/json;charset=UTF-8',
            data : JSON.stringify(data),
            dataType : "json",
            beforeSend : function(XMLHttpRequest){
                 $('body').modalmanager('loading');
             },
            success:function(mes){
                if (mes.ok == 'ok'){
                    t.parents('.btn-group').eq(0).addClass('hide');
                    t.parents('.btn-group').eq(0).prev('#btn-follow').removeClass('hide');
                    location.reload();
                }
            },
            complete:function(XMLHttpRequest,textStatus){
                // $('body').modalmanager('removeLoading').removeClass('modal-open page-overflow');
            },
            error:function(XMLHttpRequest, textStatus, errorThrown){
                $('body').modalmanager('removeLoading').removeClass('modal-open page-overflow');
                var m = JSON.parse(XMLHttpRequest.responseText)
                if(m.errnum == 300){
                    var location = window.location;
                    m.errmsg =  '还没有登录，请先 <a class="btn btn-success" href="/login?next='+ location +'">登录</a>';
                }
                $modalSYS.modal().find('.modal-body').html(m.errmsg)
            }
        })
     })


    $('#daily-from .btn').click(function() {
        rate = $('#n_rating').val()
        if(!rate){
            $('#rateword').html('请打分');
            return false;
        }else {
            return true;
        }

    })

    // 字数检查
    // 每日一评
    $('#daily-from textarea.charsFrom').NobleCount('.charsLeft',{
        on_negative: 'go_red',
        on_positive: 'go_green',
        max_chars: 140,
        on_update: function(t_obj, char_area, c_settings, char_rem){
            var form = t_obj.parents('form').eq(0),
                charsText = form.find('.charsText'),
                btn = form.find('button');
            if (char_rem < 0) {
                charsText.html('已超出');
                btn.addClass('disabled btn-default').removeClass('btn-success').prop('disabled',true)
            } else if(char_rem == 140) {
                charsText.html('还可以输入');
                btn.addClass('disabled btn-default').removeClass('btn-success').prop('disabled',true)
            } else {
                charsText.html('还可以输入');
                btn.removeClass('disabled btn-default').addClass('btn-success').prop('disabled',false)
            }
        }
    });

    // 短评字数检查
    $('#short-review-form textarea.charsFrom').NobleCount('.charsLeft',{
        on_negative: 'go_red',
        on_positive: 'go_green',
        max_chars: 140,
        on_update: function(t_obj, char_area, c_settings, char_rem){
            var dialog = t_obj.parents('.modal-dialog').eq(0),
                charsText = dialog.find('.charsText'),
                btn = dialog.find('button.btn-review-push');
            if (char_rem < 0) {
                charsText.html('已超出');
                btn.addClass('disabled btn-default').removeClass('btn-primary').prop('disabled',true)
            } else if(char_rem == 140) {
                charsText.html('还可以输入');
                btn.addClass('disabled btn-default').removeClass('btn-primary').prop('disabled',true)
            } else {
                charsText.html('还可以输入');
                btn.removeClass('disabled btn-default').addClass('btn-primary').prop('disabled',false)
            }
        }
    });

    // 个人简介
    // $('#profile-form #profile_intro').NobleCount('.charsLeft',{
    //     on_negative: 'go_red',
    //     on_positive: 'go_green',
    //     max_chars: 200,
    //     on_update: function(t_obj, char_area, c_settings, char_rem){
    //         console.log(char_rem)
    //         if (char_rem < 0) {
    //             $('#profile-from .charsText').html('已超出');
    //             $('#profile-from button').addClass('disabled btn-default').removeClass('btn-success').prop('disabled',true)
    //         } else if(char_rem == 140) {
    //             $('#profile-from .charsText').html('还可以输入');
    //             $('#profile-from button').addClass('disabled btn-default').removeClass('btn-success').prop('disabled',true)
    //         } else {
    //             $('#profile-from .charsText').html('还可以输入');
    //             $('#profile-from button').removeClass('disabled btn-default').addClass('btn-success').prop('disabled',false)
    //         }
    //     }
    // });


// ===========
// modal - 购买电影
    var $modalBuy = $('#film-buy-modal'),
        $modalBuy_body = $modalBuy.find('.modal-body');

    // 弹出窗口
    $('a[data-toggle=modal-buy]').on('click', function(){

        var buy_film_id = parseInt($(this).attr('data-film-id')),
            buy_json_data =  { film_id : buy_film_id };

        $.ajax({
            url : '/api/film/balance',
            type : 'POST',
            contentType : 'application/json;charset=UTF-8',
            data : JSON.stringify(buy_json_data),
            dataType : "json",
            beforeSend : function(XMLHttpRequest){
                 $('body').modalmanager('loading');
             },
            success:function(mes){
                if (mes.ok == false){
                    $modalBuy.find('.modal-body').html('余额不足，<a href="/account/recharge?film_id=' + buy_film_id + '">去充值</a>');
                    $modalBuy.find('.modal-footer').hide();
                    $modalBuy.modal();
                } else if(mes.ok == true){
                    $modalBuy.find('.modal-body').html('<p>确认要购买《' + mes.film.title + '》吗？</p><p>价格：'+ mes.film.price +'元</p>');
                    $modalBuy.find('.modal-footer').show();
                    $modalBuy.modal();
                }
            },
            complete:function(XMLHttpRequest,textStatus){
                 $('body').modalmanager('removeLoading');
            },
            error:function(XMLHttpRequest, textStatus, errorThrown){
                var m = JSON.parse(XMLHttpRequest.responseText)
                if(m.errnum == 300){
                    var location = window.location;
                    m.errmsg =  '还没有登录，请先 <a class="btn btn-success" href="/login?next='+ location +'">登录</a>';
                }
                $modalBuy.find('.modal-body').html('<p class="alert alert-error">' + m.errmsg + '</p>');
                $modalBuy.find('.modal-footer').hide();
                $modalBuy.modal();
            }
        })
    });

    // 确认购买
    $modalBuy.on('click', '.btn-film-buy', function(){
        
        var film_id = parseInt($(this).data('film-id'));

        //ajax
        $.ajax({
            url : '/account/recharge?film_id='+ film_id,
            type : 'POST',
            beforeSend : function(XMLHttpRequest){
                 $modalBuy_body.modalmanager('loading');
             },
            success:function(mes){
                if(mes.ok == true){
                    $modalBuy.find('.modal-footer').hide();
                    $modalBuy.find('.modal-body').html('').prepend('购买成功, 可以观看了');

                    // 1.5秒后自动关闭modal 刷新页面
                    setTimeout(function(){
                        $modalBuy.modal('hide');
                        $modalBuy.on('hidden', function(){
                            $(this).data('modal', null);
                        });
                        // window.location.reload();
                        window.location.href='/film/' + film_id + '#player';
                    }, 1500)
                }
            },
            complete:function(XMLHttpRequest,textStatus){
                 $('body').modalmanager('removeLoading');
            },
            error:function(XMLHttpRequest, textStatus, errorThrown){
                var m = JSON.parse(XMLHttpRequest.responseText)
                if(m.errnum == 300){
                    var location = window.location;
                    m.errmsg =  '还没有登录，请先 <a class="btn btn-success" href="/login?next='+ location +'">登录</a>';
                }
                $modalBuy.find('.modal-body').html('<p class="alert alert-error">' + m.errmsg + '</p>');
                $modalBuy.find('.modal-footer').hide();
                $modalBuy.modal();
            }
        })

    });

// modal - 发表短评
    var $modalReview = $('#short-review-modal'),
        $modalReview_body = $modalReview.find('.modal-body');

    // 弹出窗口
    $('a[data-toggle=modal-review]').on('click', function(){
        $('body').modalmanager('loading');
            $modalReview.modal();
            console.log($modalReview.find('textarea').size())

            setTimeout(function(){
                $modalReview.find('textarea#short_content').focus();
            },500)
    });

    // 发表短评
    $modalReview.on('click', '.btn-review-push', function(){
        var film_id = parseInt($(this).attr('data-film-id')),
            content = $('textarea#short_content').val(),
            rate = parseInt($("input#n_rating").val());

        if (!rate){ rate = 0 };

        var json_data =  { film_id : film_id, content : content, rate : rate };

        $.ajax({
            url : '/api/film/short_review_new',
            type : 'POST',
            contentType : 'application/json;charset=UTF-8',
            data : JSON.stringify(json_data),
            dataType : "json",
            beforeSend : function(XMLHttpRequest){
                 $('body').modalmanager('loading');
             },
            success:function(mes){
                if (mes.ok == false){
                    $modalReview.find('form, .modal-footer').hide();
                    $modalReview.find('.modal-body').append('<p class="alert alert-warning">出现问题</p>');
                } else if(mes.ok == true){
                    $modalReview.find('form, .modal-footer').hide();
                    $modalReview.find('.modal-body').append('<p class="alert alert-success">发布成功</p>');
                    setTimeout(function(){
                        $modalReview.modal('hide'); //发布成功后自动隐藏modal
                        location.reload()// 刷新页面
                    }, 500);
                }
            },
            complete:function(XMLHttpRequest,textStatus){
                 $('body').modalmanager('removeLoading');
            },
            error:function(XMLHttpRequest, textStatus, errorThrown){
                var m = JSON.parse(XMLHttpRequest.responseText)
                if(m.errnum == 300){
                    var location = window.location;
                    m.errmsg =  '还没有登录，请先 <a class="btn btn-success" href="/login?next='+ location +'">登录</a>';
                }
                $modalReview.find('form').hide();
                $modalReview.find('.modal-body').append('<p class="alert alert-error">' + m.errmsg + '</p>');
                $modalReview.find('.modal-footer').hide();
                $modalReview.modal();
            }
        })
    });
    
    // 关闭时 重置modal
    $modalReview.on('hidden', function(){
        $(this).find('.alert').remove();
        $(this).find('form').show();
        $(this).find('.modal-footer').show();
    });

// =======
// 回复 reply
    $('.g_reply_btn').click(function(){
        var t = $(this),
            reply_id = t.data('reply-id'),
            p_username = t.parents('li').eq(0).find('.m_n_item_info a').eq(1).text(),
            p_user_link = t.parents('li').eq(0).find('.m_n_item_info a').eq(1).attr('href'),
            cont = t.parents('li').eq(0).find('p').text();

        if( cont.length > 35 ){
            cont = cont.substr(0,35) + '...';
        }

        $('#reply_form .is_reply p').html(cont);
        $('#reply_form .is_reply span a').attr('href',p_user_link).html(p_username);
        $('#parent_id').val(reply_id);
        $('#reply_form .is_reply').removeClass('hide');
        $(document).stop().scrollTo('#reply_form', 400);
        $('#reply_form textarea').focus();
    })

    $('.is_reply .close').click(function(){
        $('#parent_id').val('-1');
        $(this).parents('.is_reply').addClass('hide');
    })


// item_cover hover
    $('.item_cover, .pay_f').hover(function(){
        $(this).parents('li').eq(0).find('.item_cover').addClass('active');
    },function(){
        $(this).parents('li').eq(0).find('.item_cover').removeClass('active');
    })

// auto hide alerts
    setTimeout(function(){
        $('#alerts').slideUp();
    },1200)

//页面滚动
    $(window).scroll(function() {
        //导航和回顶部的显隐
        var t = $(window).scrollTop();
        console.log(t)
        if(t > 1024){
            $('#goTop').fadeIn();
        }
        if (t <= 1024){
            $('#goTop').fadeOut();
        }
    })

// 回顶端 
    $('#goTop').click(function(){
        $(document).stop().scrollTo(0, 400);
    })

// check Browser
    function showBrowserTip(){
        $('#browser').show().html('我们发现您当前使用的浏览器比较旧了，推荐您升级浏览器，或者使用Chrome、火狐等高级浏览器来访问我们的网站');
    }
    function isBrowser(){
        var Sys={};
        var ua=navigator.userAgent.toLowerCase();
        var s;
        (s=ua.match(/msie ([\d.]+)/))?Sys.ie=s[1]:
        (s=ua.match(/firefox\/([\d.]+)/))?Sys.firefox=s[1]:
        (s=ua.match(/chrome\/([\d.]+)/))?Sys.chrome=s[1]:
        (s=ua.match(/opera.([\d.]+)/))?Sys.opera=s[1]:
        (s=ua.match(/version\/([\d.]+).*safari/))?Sys.safari=s[1]:0;
        if(Sys.ie){//Js判断为IE浏览器
            if(Sys.ie=='10.0'){
                // nothing to do
            }else if(Sys.ie=='9.0'){
                //Js判断为IE 9
            }else if(Sys.ie=='8.0' || Sys.ie=='7.0' || Sys.ie=='6.0'){
                //Js判断为IE 8
                showBrowserTip()
            }
        }
        if(Sys.firefox){
            //Js判断为火狐(firefox)浏览器
            // nothing to do
        }
        if(Sys.chrome){
            //Js判断为谷歌chrome浏览器
            // nothing to do
        }
        if(Sys.opera){
            //Js判断为opera浏览器
            // nothing to do
        }
        if(Sys.safari){
            //Js判断为苹果safari浏览器
            // nothing to do
        }
    }

    isBrowser()

})