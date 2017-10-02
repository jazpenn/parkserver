$(function(){
	$('.comment_del').click(function(){
		if( !confirm('确定要删除吗?') ) return false;
	})
})