$(function(){
	$('.group_del').click(function(){
		if( !confirm('确定要删除吗?') ) return false;
	})


	$('.group_pic').mouseover(function(){
			$(this).find('a').css('display','block')
	}).mouseout(function(){
			$(this).find('a').css('display','none')
		});


})