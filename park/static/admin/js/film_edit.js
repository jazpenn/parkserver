$(function(){
	$('#film_edit').submit(function(event){

		title = $('.film_title').val();		
		url = $('.film_url').val();		
		rate = $('.film_rate').val();
		price = $('.film_price').val();

		re = /^[0-9]+.?[0-9]$/;
		if( !title ) edit_tips(event,'title');
		else if( !url ) edit_tips(event,'url');
		else if( !rate ) edit_tips(event,'rate');
		else if( !re.test(rate) ) edit_tips(event,'rate_int');
		// else if( price && !re.test(price) && price > 0 ) edit_tips(event,'price_int');



	});

	$('.reset').click(function(){
		if( !confirm('确定要重置吗?') ) return false;
	})


	function edit_tips( e, type ){
		tips = {
				'title' : '标题不能为空',
				'url' : '播放地址不能为空',
				'rate' : '评分不能为空',
				'rate_int' : '评分必须为整数或浮点数',
				'price_int' : '价格必须为整数或浮点数',
				'unknown' : '未知错误'
			}
		switch( type ){
			case 'title':
				alert( tips['title'] );
				e.preventDefault();
				return;
			case 'url':
				alert( tips['url'] );
				e.preventDefault();
				return;
			case 'rate':
				alert( tips['rate'] );
				e.preventDefault();
				return;
			case 'rate_int':
				alert( tips['rate_int'] );
				e.preventDefault();
				return;
			case 'price_int':
				alert( tips['price_int'] );
				e.preventDefault();
				return;
			default:
				alert( tips['unknown'] );
				e.preventDefault();
		}
	}
})

