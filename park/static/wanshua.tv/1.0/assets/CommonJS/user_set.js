
user_set = {}

user_set.sets = function(){

    $(function(){

        user_sets = new Vue({
            el: '.settings-content',
            ready: function () {

            },
            data: {
                username: G_USER.username,
                new_gender: G_USER.new_gender,
                avatar: G_USER.avatar,
                avatar_pending: false
            },
            computed: {

            },
            methods: {
                updateUser: function () {
                    var values = {
                        username: this.username,
                        new_gender: this.new_gender,
                        avatar: this.avatar
                    };

                    $.post('/api/user/edit', values, function (res) {
                        console.log(res);
                        G_USER.username = res.user.username;
                        G_USER.avatar = res.user.avatar;
                        G_USER.new_gender = res.user.new_gender;
                    });
                },
                stopEvent: function(event){
                    event.preventDefault();
                    event.stopPropagation();
                }
            }
        });


        AVATAR_DOMAIN = 'http://7xnm2g.com2.z0.glb.qiniucdn.com/';

        function upload_avatar() {

            the_avatar = $("#change-avatar")[0].files[0];

            var acceptedTypes = {
                "image/gif": true,
                "image/jpeg": true,
                "image/png": true
            };

            if (acceptedTypes[the_avatar.type] != true) {
                swal("提示", "图片格式错了啦~");
                return;
            }

            Qiniu_UploadUrl = "http://upload.qiniu.com/";

            $.post('/qiniu/avatar/token', {}, function (data) {

                var formData = new FormData();

                formData.append('token', data.uptoken);
                formData.append('key', data.save_key);
                formData.append('file', the_avatar);

                var xhr = new XMLHttpRequest();
                xhr.open('POST', Qiniu_UploadUrl);

                xhr.onload = function () {
                    if (xhr.status === 200) {
                        _response = JSON.parse(xhr.response);
                        user_sets.avatar = AVATAR_DOMAIN + _response.key + '-avatar';
                        user_sets.avatar_pending = false;
                    }
                };

                user_sets.avatar_pending = true;

                xhr.send(formData);

            });

        };

        $("#change-avatar").on("change", function (event) {

            upload_avatar();

        });


    });

};

user_set.billing = function(){

    $(function(){

        user_billing = new Vue({
            el: ".settings-content",
            ready: function () {

                var that = this;

                $.get('/apis/charge/category', function(data){

                    that.charge_list = data.data.categorys;

                });

            },
            data: {
                cur_charge: 0,
                charge_list: null,
                charge_method: 'alipay_pc_direct'
            },
            computed: {

            },
            methods: {
                charge_submit: function () {

                    var charge_values = {
                        channel: this.charge_method,
                        category_id: this.charge_list[this.cur_charge].id
                    };

                    $.post("/charge", charge_values, function (res) {
                        console.log(res);
                        pingppPc.createPayment(res, function (result, err) {
                            console.log(result, err);
                            alert('服务出错.');
                        });
                    });

                }
            }
        });

    });

};


user_set.password = function(){

    $(function(){

        
        
    });

};

module.exports = user_set;