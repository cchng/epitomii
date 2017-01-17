(function($) {

    $('#postModal').on('show.bs.modal', function (e) {
	$.ajax({
            url: "/show_post",
            data: $(e.relatedTarget).data('src'),
	    contentType: "text/plain",
            type: 'POST',
            success: function(response) {
		$('#postContent').html(response);
            },
            error: function(error) {
                console.log(error);
            }
        });

    });

})(jQuery);
