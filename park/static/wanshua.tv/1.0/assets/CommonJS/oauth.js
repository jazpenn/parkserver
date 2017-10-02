
oauth = {};

oauth.send_code = function(){

    send_code = new Vue({
        el: '.phone-number:not(.login)',
        data: {
           phone: null 
        },
        methods: {
            send_code: function(type){

                var that = this;

                if (!that.phone) return;

                var values = {
                    phone: that.phone,
                    type: type
                };

                $.post('/api/vertify/code', values, function(data){
                   $('#validate-btn').attr('disabled', 'true').text('已发送');
                });

            }
        }
    });

};

oauth.login = function(){

};

oauth.signup = function(){

};

oauth.findpwd = function(){

};

module.exports = oauth;