$(function(){

	$('.film_pic').mouseover(function(){
			$(this).find('a').css('display','block')
	}).mouseout(function(){
			$(this).find('a').css('display','none')
		});


})