$(function(){
	$('.reset').click(function(){
		if( !confirm('确定要重置吗?') ) return false;
	})

	$('.group_img a').click(function(){
		if( !confirm('确定要删除吗?') ) return false;
	})
})