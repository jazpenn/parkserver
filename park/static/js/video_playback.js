$(function () {

    //  播放器相关 


    Vue.config.delimiters = ["[[", "]]"];

    Video = new Vue({
        el: '.main-content',
        ready:function () {

        },
        data: {
            global_user:curr_user,
            reply_words: '',
            is_follow: is_follow,
            follower_count:user.follower_count,
            live_user_count:live.live_user_count,
            replys:_replys,
            live:live
        },
        computed: {

        },
        methods: {


            sendReply: function () {

                if (!this.reply_words) return;

                if (!Video.global_user) {

                    $('#modal-login').modal('show');
                    return;
                }

                var data = {
                    live_id:Video.live.uid,
                    content:this.reply_words
                };
                
               
                $.post('/api/live/reply/new', data, function (rep) {

                    if (rep.reply) {

                        Video.replys.push(rep.reply);
                    };

                    alert("hello");

                });

                 Video.reply_words = '';


            },


            followSwitch:function(){

                if (!Video.global_user) {
                    $('#modal-login').modal('show');
                    return;
                }

               
                
                if (this.is_follow){

                    var data = {
                        action:'unfollow',
                        user_id:user.uid
                    };

                    $.post('/api/user/follow',data,function(rep){

                        if(rep.errmsg){
                            alert(rep.errmsg);
                            return;
                        }

                        Video.is_follow = false;

                        if (rep.follower_count >= 0) {
                            Video.follower_count = rep.follower_count;
                        };

                    });
     

                }
                else {

                    var data = {
                        action:'follow',
                        user_id:user.uid
                    };

                   

                    $.post('/api/user/follow',data,function(rep){

                        if(rep.errmsg){
                            alert(rep.errmsg);
                            return;
                        }

                        Video.is_follow = true;

                        if (rep.follower_count >= 0) {
                            Video.follower_count = rep.follower_count;
                        };

                    });
                    
                    
                }

            }


        }
    });


})
