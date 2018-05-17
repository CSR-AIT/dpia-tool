// <!-- AddModal Script -->
$(".add").click(function(ev) { // for each edit edit url
  ev.preventDefault(); // prevent navigation
  var url = $(this).data("form"); // get the edit form url
  $("#addModal").load(url, function() { // load the url into the modal
    $(this).modal('show'); // display the modal on url load
  });
  return false; // prevent the click propagation
});


// <!-- AddModal Script -->
// $(".add-primary").click(function(ev) { // for each edit edit url
//   ev.preventDefault(); // prevent navigation
//   var url = $(this).data("form"); // get the edit form url
//   $("#addModal2").load(url, function() { // load the url into the modal
//     $(this).modal('show'); // display the modal on url load
//   });
//   return false; // prevent the click propagation
// });
