var like = function(event){

	console.log('hi')
	post_id = event.srcElement.attributes["data-id"].nodeValue;
	console.log(post_id)

	status_message = $('.likes__button-message[data-id="' + post_id + '"]')

	$.ajax(
		{
			type: 'POST',
			url: '/blog/' + 'like/' + post_id + '/',
			beforeSend: function(xhr, settings){
				status_message.css('color', 'black').html('Liking...');
			},
			success: function(data){
				var likes_el = $('.likes[data-id="' + post_id + '"]');
				likes_el.html(data);
			},
			error: function(xhr, status){
					status_message.css('color', 'red').html('Error processing request.');
			}
		}
	);

}

var comment = function(event){

	post_id = event.srcElement.attributes["data-id"].nodeValue;
	console.log(post_id)

	$.ajax(
		{
			type: 'POST',
			url: '/blog/' + 'comment/' + post_id + '/',
			data: $('.comments__textarea').val(),
			contentType: 'text/plain',
			beforeSend: function(xhr, settings){
				$('.comments__submit-status').css('color', 'black').html('Sending...');
			},
			success: function(data, status, xhr){
				$('.comments__submit-status').css('color', 'green').html('Success!');
				var comment_el = $('.comments__list[data-id="' + post_id + '"]');
				new_comment = comment_el.append(data);
				new_comment.addClass('comments__freshly-posted');
			},
			error: function(xhr, status){
				if (xhr.status == 403){
					$('.comments__submit-status').css('color', 'red').html('You must <a href="/blog/login/">sign in</a> or <a href="/blog/signup/">create an account</a> to comment.');
				} else if (xhr.status == 422){
					$('.comments__submit-status').css('color', 'red').html('');
				} else {
					$('.comments__submit-status').css('color', 'red').html('Error processing request.');
				}
			}
		}
	);

}

$('.likes__submit').on('click', '.likes__button', function(event){
	like(event);
});

$('.comments__wrapper').on('click', '.comments__submit-button', function(event){
	text = $('.comments__textarea').val();
	console.log(text);
	if(text != ''){
		comment(event);
	}
});
