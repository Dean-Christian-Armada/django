$(document).ready(function(){
	$('#likes').click(function(){
		var catid;
		catid = $(this).attr("data-catid");
		$.get('/rango/like_category/', {category_id: catid}, function(data){
			$('#like_count').html(data);
			$('#likes').hide();
		});
	});
	$('#suggestion').keyup(function(){
		var query;
		query = $(this).val();
		$.get('/rango/suggest_category/', {suggestion: query}, function(data){
			// alert(data);
			$('#cats').html(data);
		});
	});
	$('.rango-add').click(function(){
		// alert('dean');
		var catid;
		var title;
		var url;
		catid = $(this).attr("data-catid");
		title = $(this).attr("data-title");
		url = $(this).attr('data-url');
		$.get('/rango/auto_add_page/', { category_id: catid, url: url, title: title }, function(data){
			// alert(data);
			$('#pages').html(data);
		});
	});
	$('.rango-delete').click(function(){
		var pageid;
		var catid;
		catid = $(this).attr('data-catid');
		pageid = $(this).attr('data-pageid');
		// alert(pageid+' '+catid);
		$.get('/rango/auto_delete_page/', { category_id: catid, page_id: pageid }, function(data){
			// alert(data);
			$('#pages').html(data);
		});
	});
	$('#dean').click(function(){
		alert('dean');
	})
});
