$(document).ready(function() {
    // Handle login form submission
    $('#login-form').submit(function(e) {
    e.preventDefault();  // prevent default form submission

    // Serialize form data into a JSON object
    var formData = JSON.stringify($(this).serializeArray());

    // Send AJAX request to server
    $.ajax({
        type: 'POST',
        url: '/',
        data: formData,
        contentType: 'application/json',
        dataType: 'json',
        success: function(response) {
        // Redirect to homepage on successful login
        window.location.href = '/home';
        },
        error: function(response) {
        // Display errors in login form
        $('#login-errors').html('<div class="alert alert-danger">' + response.responseJSON.message + '</div>');
        }
    });
    });
});
