$(function(){
	$('#tag_edit').submit(function(event){
		name = $('.tag_name').val();		
		if( !name ) edit_tips(event,'name');

	});

	$('.reset').click(function(){
		if( !confirm('确定要重置吗?') ) return false;
	})


	function edit_tips( e, type ){
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

