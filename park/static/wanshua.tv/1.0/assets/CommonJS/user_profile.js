
user_profile = {};

user_profile.profile = function(){

    user_profile = new Vue({

         el: '.profile-content',
            ready: function () {

            },
            data: {
                user: USER,
                is_current: IS_CURRENT,
                is_follow: IS_FOLLOW
            },
            computed: {
            },
            methods: {
                
                follow_user: function(){

                    var that = this;

                    var action = this.is_follow?'unfollow':'follow';

                    var values = {
                        user_id: this.user.uid,
                        action: action
                    };

                    $.post('/api/user/follow', values, function(data){

                        that.is_follow = !that.is_follow;

                    });


                }


            }

    });

};

module.exports = user_profile;