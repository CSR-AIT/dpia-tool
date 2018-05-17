// Confirmation jQuery
$('.confirmation').on('click', function () {
    return confirm('Are you sure?');
});


$("#menu-toggle").click(function(e) {
    e.preventDefault();
    $("#wrapper").toggleClass("active");
});
