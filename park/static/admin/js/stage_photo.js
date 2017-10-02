$(function(){

	$('.stage_photo img').click(function() {

		var img_url = $(this).attr('src')
		var covers = cover('id','cover',100);
		$('body').append( covers ).append('<img id="img_big" src="'+ img_url +'" />')
		$('#cover').css({'opacity':0.5,'background':'#ccc'}).width(document.width).height(document.height).click(function(){
			$(this).remove();
			$('#img_big').remove();
		})
		center('#img_big')
		$('#img_big').css({'zIndex':200})
		if($('#img_big').height() > $(window).height()) {
			$('#img_big').css({'top':0})
		}


	})
	$('.stage_photo').mouseover(function() {
		$(this).find('.del_but').css('display','block');
	}).mouseout(function() {
		$(this).find('.del_but').css('display','none');
	});


	$('.del_but').click(function(){
		if( !confirm('确定要删除吗?') ) return false;
	})



	/**
	 *	生成div背影
	 *	@param div的属性类型;
	 *	@param div的属性值
	 *
	 */
	function cover($type,$cover,index){
		$div=('<div '+$type+'="'+$cover+'" style="z-index:'+index+';position:absolute;height:100%;width:100%;top:0;left:0;"></div>');
		return $div;
	}


	/**
	 *	居中
	 *	@param 选择器名字
	 *
	 */
	function center($name){
		$($name).css({'position':'absolute','top':'0','left':'0'});
		$d_width=$(window).width();		//获取浏览器的宽
		$d_height=$(window).height();		//获取浏览器的高
		$l_height=$($name).css('height');
		$l_width=$($name).css('width');

		//让div居中
		$width=($d_width-parseInt($l_width))/2;
		$height=($d_height-parseInt($l_height))/3;
		$($name).css({'left':$width+'px'});
		$($name).css({'top':$height+'px'});
	}




})