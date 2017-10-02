$(function () {

    //  播放器相关 

    function loadedHandler() {

    }
    var flashvars = {
        f: rtmp_play_url,
        p: 1,
        loaded: 'loadedHandler',
        b: 0
    };
    var params = {
        bgcolor: '#FFF',
        allowFullScreen: true,
        allowScriptAccess: 'always',
        wmode: 'transparent'
    };
    var video = [hls_play_url];

    CKobject.embed('/static/ckplayer/ckplayer.swf', 'player', 'ckplayer_player', '100%', '480', false, flashvars, video, params);


    // // 弹幕部分

    MessageItem = function (values) {
        this.uid = values.uid;
        this.username = values.username;
        this.content = values.content;
        this.color = values.color;
        this.role = values.role;
        this.pic = values.pic;
    };

    DanmakuItem = function (values) {
        this.mode = 1;
        this.text = values.username + ': ' + values.content;
        this.size = 18;
        this.color =  0xffffff;
        this.dur = 8000;
        
    };

    var CM = new CommentManager(document.getElementById('danmaku_container'));
    CM.init();
    CM.start();
    window.CM = CM;


    function statusChange(status){
        console.log(status,'=========');
    };

    function extraParams(){

        var a = {token:jwt_token};
        return a;
    };

    // function messageReceived(){

    // };

    // var pushstream = new PushStream({
    //   host: '182.92.152.61',
    //   port: 9080,
    //   modes: "longpolling",
    //   reconnectOnTimeoutInterval:500
    // });
   
    // pushstream.onmessage = messageReceived;
    // pushstream.extraParams = extraParams;
    // pushstream.onstatuschange = statusChange;
    // pushstream.addChannel(room);
    // pushstream.connect();

    // console.log(room,'============');


    Vue.config.delimiters = ["[[", "]]"];



    var chatWindow = $('#chatWindow');

    Vue.transition('scroll-bottom', {
      
      afterEnter: function (el) {
            chatWindow.scrollTop(chatWindow[0].scrollHeight);
      }

    });


     Living = new Vue({
        el: '.wrapper',
        ready:function () {

            this.pushstream = new PushStream({
                host: '101.200.144.186',
                port: 80,
                modes: "longpolling",
                reconnectOnTimeoutInterval:100
            });

            this.pushstream.onmessage =  this.messageReceived;
            this.pushstream.onstatuschange = statusChange; // for test
            this.pushstream.extraParams = extraParams;
            this.pushstream.addChannel(room);
            this.pushstream.connect();


        },
        data: {
            global_user:curr_user,
            pushstream:null,
            danmu_words: null,
            danmu_list: chats,
            is_follow: is_follow,
            user_balance:curr_user ? curr_user.balance : 0,
            follower_count:user.follower_count,
            live_user_count: live ? live.live_user_count: 0,
            status:status,
            danmu_ctl:true,
            user_id:uid,
            user:user,
            showErrMsg:false,
            errMsg:''
        },
        computed: {

        },
        methods: {
            messageReceived: function(text,id,channel){

                // 有新的评论
                if ("new comment" in text) {

                    var message = new MessageItem(text['new comment']);

                    if (Living.danmu_list.length > 200) {

                        Living.danmu_list.shift();
                    }

                    Living.danmu_list.push(message);

                    if (Living.danmu_ctl) {

                        Living.sendDanmaku(message);
                    };


                };

                // 直播结束
                if ( "ended" in text) {

                    Living.status = 'disconnected';

                };
                
                // 房间信息发生改变 

                if ("room info"  in text) {

                    if(text['room info'].live_user_count >= 0){

                        Living.live_user_count = text['room info'].live_user_count;
                    }

                };


            },

            sendReply: function () {

                if (!this.danmu_words) return;

                if (!Living.global_user) {

                    $('#modal-login').modal('show');
                    return;
                }

                var data = {
                    user_id: user_id,
                    room: room,
                    username: username,
                    content: this.danmu_words
                };
                
                Living.danmu_words = '';

                $.post('/api/room/chat', data, function (rep) {

                    if (rep.errmsg) {
                        Living.showErrMsg = true;
                        Living.errMsg = rep.errMsg

                        setTimeout(function() {

                            Living.showErrMsg = false;
                            Living.errMsg = "";
                        }, 2000);

                    }

                    console.log(rep);
                    console.log(rep.errmsg);
                });

            },

            sendDanmaku: function (message) {
                var _danmaku = new DanmakuItem(message);
                
                if(message.color == 'red'){
                    _danmaku.color = 0xee3221;
                }
                
                CM.send(_danmaku);
            },

            rewardGift:function(gift_id){
                
                var data = {gift_id:gift_id,user_id:user.uid};
                
                
                if (!Living.global_user) {

                   $('#modal-login').modal('show');
                    return;
                }
                
                $.post('/api/reward/gift', data, function (rep) {
                    //  live_play.sendDanmaku(new MessageItem(username, live_play.reply_words));
                    
                    if(rep.errmsg){
                        alert(rep.errmsg);
                        return;
                    }
                    
                    if(rep.balance){
                        Living.user_balance = rep.balance;
                    }

                });
                
            },

            followSwitch:function(){

                if (!Living.global_user) {
                    $('#modal-login').modal('show');
                    return;
                }

               
                
                if (this.is_follow){

                    var data = {
                        action:'unfollow',
                        user_id:user.uid
                    };

                    console.log(data);

                    $.post('/api/user/follow',data,function(rep){

                        if(rep.errmsg){
                            alert(rep.errmsg);
                            return;
                        }

                        Living.is_follow = false;

                        if (rep.follower_count >= 0) {
                            Living.follower_count = rep.follower_count;
                        };

                    });
     

                }
                else {

                    var data = {
                        action:'follow',
                        user_id:user.uid
                    };

                    console.log(data);

                    $.post('/api/user/follow',data,function(rep){

                        if(rep.errmsg){
                            alert(rep.errmsg);
                            return;
                        }

                        Living.is_follow = true;

                        if (rep.follower_count >= 0) {
                            Living.follower_count = rep.follower_count;
                        };

                    });
                    
                    
                }

            }


        }
    });


})
