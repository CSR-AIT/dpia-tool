var frm = $('#add_primary');
frm.submit(function () {
  $.ajax({
      type: frm.attr('method'),
      url: frm.attr('action'),
      data: frm.serialize(),
      dataType: "json",
      success: function (data) {
        $('.primaries').append($('<option>', {
            value: data.id,
            text: data.name
        }));
        // $('.primaries').val(data.id)
        var primary_name = data.name;
        // alert('Primary Asset added successfully.');
        $("#myModal").fadeOut();
        $('.modal-backdrop').remove();
        // $('.outer_success').addClass("alert alert-success center m-b-5 m-t-1")
        $('.inner_success').append('<i class=fa>&#xf058;</i> Primary Asset ' + primary_name + ' was added successfully. ');
        // setTimeout(function(){
        //   $('div.outer_success').fadeOut();
        // }, 5000);
      },

      error: function(data) {
        $('div.inner_error').replaceWith("A Primary Asset with that description already exists.");
        $('div.outer_error').addClass("alert alert-danger fade in");

      }
  });
  return false;
});
