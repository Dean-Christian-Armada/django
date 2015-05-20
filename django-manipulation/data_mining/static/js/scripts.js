$(document).ready(function() {
	$(".add-btn").click(function(){
		$('#dialog').dialog('open');
	});
	$(".update-form").click(function(){
		id = $(this).attr('data-catid');	
		$.get(update_form, { update_id: id }, function(data){
			$('#update-dialog').html(data);
		});
		setTimeout(function(){ $('#update-dialog').dialog('open'); }, 300);
	});
	$(".delete-btn").click(function(){
		id = $(this).attr('data-catid');
		$.get(delete_url, { id: id }, function(data){
			$('.members').html(data);
		});
	});
	$( "#dialog" ).dialog({
		// bool variable found in add_member.html
		autoOpen: bool,
		modal: true,
		width: 'auto',
		closeOnEscape: true,
		draggable: false,
	});	
	$( "#update-dialog" ).dialog({
		autoOpen: false,
		modal: true,
		width: 'auto',
		closeOnEscape: true,
		draggable: false,
	});
	$('#search').keyup(function(){
		name = $(this).val();
		$.get(search_url, { name: name }, function(data){
			$('.members').html(data)
		});
	});
	$('table.table td').click(function(){
		value = $(this).text();
		selector = $(this).index();
		name = $(this).siblings('td:nth-child(3)').text();
		var update = $( "#update-dialog" ).dialog({
			title: "Updating "+name,
		});	
	});
});