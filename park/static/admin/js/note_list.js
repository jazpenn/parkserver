$(function(){
	$('.note_del').click(function(){
		if( !confirm('确定要删除吗?') ) return false;
	})

	$('.view_content').click(function(){
		var s_content = $(this).data('content');
		var d_width = $(document).width();
		var d_height = $(document).height();
		var w_width = $(window).width();
		var w_height = $(window).height();
		var o_view = $('.view_content_box');
		var v_width = o_view.width();
		var v_height = o_view.height();
		if(v_height > w_height) {
			o_view.css({'left':(w_width-v_width)/2,'display':'block'});
		} else {
			o_view.css({'left':(w_width-v_width)/2, 'top':(w_height-v_height)/2,'display':'block'});
		}
		o_view.find('.contents').html(s_content);

	})

	$('.close').click(function(){
		$('.view_content_box').css('display','none');
	})




})