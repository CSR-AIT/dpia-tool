$(function () {

  /* Functions */

  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-primary").modal("show");
      },
      success: function (data) {
        $("#modal-primary .modal-content").html(data.html_form);
      }
    });
  };


  var saveForm = function () {
    var form = $(this);
    $.jGrowl.defaults.closer = false;

    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      params: {
                'csrf_token': '{{ csrf_token }}',
                'csrf_name': 'csrfmiddlewaretoken',
                'csrf_xname': 'X-CSRFToken',
              },
      success: function (data) {
        if (data.form_is_valid) {
          $('.actors').append($('<option>', {
              value: data.id,
              text: data.name
          }));
          $("#modal-primary").modal("hide");
          $.each(data.messages, function (i, m) {
            $.jGrowl(m.message, {
              position: 'top-right',
              sticky: false,
              openDuration: 'fast',
              theme: 'success',
              // header: '<i class=fa fa-fw>&#xf058;</i> Success',
            });
          });
        }
        else {
          $("#modal-primary .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };


  // Create Primary Asset
  $(".js-add-actor").click(loadForm);
  $("#modal-primary").on("submit", ".js-actor-add-form", saveForm);

});
