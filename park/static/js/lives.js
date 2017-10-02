$(function () {




    Vue.config.delimiters = ["[[", "]]"];


    Index = new Vue({
        el: '#index-content',
        ready:function () {



        },
        data: {
            global_user:curr_user,
            page:2,
            loading:false,
            lives:_lives,
            loadmore:true
        },
        computed: {

        },
        methods: {

            loadMore:function(){

                var data = {
                    page:Index.page
                }

                Index.loading = true;

                $.get('/api/live/loadmore',data,function(rep){



                    if(rep.errmsg){
                        alert(rep.errmsg);
                        return;
                    }

                    Index.loading = false;

                    if (!rep.lives) {
                        Index.loadmore = false;

                        return;
                    };

                    console.log(rep.lives);

                    $.each(rep.lives,function(key,value){

                        Index.lives.push(value);
                    });
                    

                    Index.page = rep.page + 1;


                });

            }

        }
    });


})
