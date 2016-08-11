/* global $ */

var like = function(event){

	var post_id = event.srcElement.attributes["data-id"].nodeValue;

	var status_message = $('.likes__button-message[data-id="' + post_id + '"]');

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

};

var comment = function(event){

	var post_id = event.srcElement.attributes["data-id"].nodeValue;

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
				var new_comment = comment_el.append(data);
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

};


$('.likes__submit').on('click', '.likes__button', function(event){
	like(event);
});

$('.comments__wrapper').on('click', '.comments__submit-button', function(event){
	var text = $('.comments__textarea').val();
	if(text != ''){
		comment(event);
	}
});




var editComment = function(event){
	var comment_id = event.srcElement.attributes["data-comment"].nodeValue;
	console.log(comment_id);
};

var deleteComment = function(event){
	var comment_id = event.srcElement.attributes["data-comment"].nodeValue;
	console.log(comment_id);
};

$('.comments__comment-edit').on('click', function(event){
	editComment(event);
});

$('.comments__comment-delete').on('click', function(event){
	deleteComment(event);
});
