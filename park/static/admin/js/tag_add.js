$(function(){
	$('#tag_add').submit(function(event){
		name = $('.tag_name').val();		
		if( !name ) add_tips(event,'name');

	});

	$('.reset').click(function(){
		if( !confirm('确定要重置吗?') ) return false;
	})


	function add_tips( e, type ){
		tips = {
				'name' : '标签名不能为空',
				'unknown' : '未知错误'
			}
		switch( type ){
			case 'name':
				alert( tips['name'] );
				e.preventDefault();
				return;
			default:
				alert( tips['unknown'] );
				e.preventDefault();
		}
	}
})

