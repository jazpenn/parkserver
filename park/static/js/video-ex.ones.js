
function time_format (time) {
    time = parseInt(time);
    var minutes = parseInt(time/60);
    var seconds = time%60;
    minutes = minutes<10?'0'+minutes:minutes;
    seconds = seconds<10?'0'+seconds:seconds;
    return minutes+':'+seconds
}

function progress_bar_click_progress (event, target_el) {
    return (event.clientX-target_el.offset().left)/target_el.width();
}

$(function(){
	video_width = $("#video_player").width();
	origin_width = 330;
	origin_height = 186;
	player_height = video_width / origin_width * origin_height;

	video_player = videojs('video_player', {
		height: player_height,
		autoplay: true,
		controls: false,
		flash: {
			swf: '/static/video-js.swf'
		}
	});
	$('#video_player').bind('contextmenu',function() { return false; });

	$("#video_play_board .rotate_btn").insertAfter("#video_player video");
	$("#video_player").hover(function() {
		$("#video_play_board .rotate_btn").stop().fadeIn()
	}, function() {
		$("#video_play_board .rotate_btn").fadeOut(3800)
	});

	html5_video_player = $("#video_player video");
	var this_video_height = "height";
	var deg_num = 90;
	$("#video_play_board .rotate_btn").click(function() {
		if ("height" == this_video_height) {
			html5_video_player.css("width", html5_video_player.height()).addClass("html5_video_center");
			this_video_height = "width";
		} else {
			html5_video_player.removeAttr("style").removeClass("html5_video_center");
			this_video_height = "height";
		}
		html5_video_player.css("transform", "rotate(" + deg_num + "deg)");
		deg_num += 90;
		deg_num %= 360;
	});

	video_player.on("fullscreenchange", function(){
		html5_video_player.removeAttr("style").removeClass("html5_video_center");
		this_video_height = "height";
		deg_num = 90;
	});

	if (window.screen.availWidth<992) {
        video_player.controls(true);
    }

    $('#danmaku_and_player').height(player_height);
    CM = new CommentManager(document.getElementById('danmaku_container'));
    CM.init();

    Vue.config.delimiters = ["[[", "]]"];

    new_controls = new Vue({
      el: '#new_controls',
      data: {
        video_id: null,
        danmaku_text: null,
        progress_loaded: 0,
        progress_played: 0,
        is_playing: true,
        no_voice: false,
        volume_value: 0.38,
        video_total_time: 0,
        video_cur_time_str: '00:00',
        video_total_time_str: '00:00',
        video_progress_bar: $("#video_progress_bar"),
        voice_progress_bar: $("#voice_progress_bar"),
        text_size: 24,
        danmu_type: 1,
        cur_color: 16777215,
        font_block: $('#font_block'),
        hot_block: $('#hot_block'),
        danmaku_input: $('#danmaku_input'),
        fonts: [],
        types: [],
        colors: [],
        hots: []
      },
      methods: {
        play_click: function(){
            video_player.play();
            new_controls.is_playing = true;
        },
        pause_click: function(){
            video_player.pause();
            new_controls.is_playing = false;
            CM.stop();
        },
        voice_click: function(){
            if (new_controls.no_voice){
                video_player.volume(new_controls.volume_value);
                new_controls.no_voice = false;
            }
            else {
                video_player.volume(0);
                new_controls.no_voice = true;
            }
        },
        input_focus: function(){
            new_controls.font_block.hide();
            new_controls.hot_block.hide();
        },
        progressbar_click: function(event){
            video_player.currentTime(progress_bar_click_progress(event, new_controls.video_progress_bar)*new_controls.video_total_time);
        },
        voicebar_click: function(event){
            new_controls.volume_value = progress_bar_click_progress(event, new_controls.voice_progress_bar);
            video_player.volume(new_controls.volume_value);
        },
        full_screen_click: function(){
            video_player.requestFullscreen();
        },
        send_danmaku: function(){
            if (!new_controls.danmaku_text)
                return;
            var current_time = video_player.currentTime();
            var total_time = video_player.duration();
            var danmu_time = current_time==total_time?total_time-1:current_time;
            $.post("/api/video/danmu/new", {video_id:new_controls.video_id, content:new_controls.danmaku_text, time:danmu_time,danmu_type:new_controls.danmu_type, text_size:new_controls.text_size, color:new_controls.cur_color}, function(data){
                new_controls.danmaku_text = '';
                CM.send(data.danmu);
            });
        },
        font_block_ctl: function(){
            new_controls.font_block.toggle();
            new_controls.hot_block.hide();
        },
        hot_block_ctl: function(){
            new_controls.hot_block.toggle();
            new_controls.font_block.hide();
        },
        font_click: function(font_item){
           console.log(font_item.value);
           new_controls.text_size=font_item.value;
        },
        type_click: function(type_item){
            console.log(type_item.value);
            if (new_controls.danmu_type==type_item.value)
                new_controls.danmu_type=1;
            else new_controls.danmu_type=type_item.value;
        },
        color_click: function(color_item){
           console.log(color_item.value, new_controls.cur_color);
           new_controls.cur_color=color_item.value;
        },
        hot_click: function(hot_item){
            new_controls.danmaku_text=hot_item.words;
            new_controls.hot_block.toggle();
            new_controls.danmaku_input.focus();
        }
      }
    });

    video_player.on("play", function(){
        CM.start();
    });

    video_player.on("timeupdate", function(){
        var current_time = video_player.currentTime();
        CM.time(current_time);
        new_controls.video_cur_time_str = time_format(current_time);
        new_controls.progress_played = current_time/new_controls.video_total_time*100;
        if (new_controls.progress_played==100)
            new_controls.is_playing = false;
        if (!new_controls.video_total_time){
            new_controls.video_total_time = video_player.duration();
            new_controls.video_total_time_str = time_format(new_controls.video_total_time);
        }
    });

    video_player.on("loadedmetadata", function(){
        new_controls.video_total_time = video_player.duration();
        new_controls.video_total_time_str = time_format(new_controls.video_total_time);
    });

    video_player.on("loadeddata", function(){
        new_controls.progress_loaded = video_player.bufferedPercent()*100;
    });

    video_player.on("loadedalldata", function(){
        new_controls.progress_loaded = video_player.bufferedPercent()*100;
    });

});
