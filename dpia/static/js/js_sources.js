$(function () {

  /* Functions */

  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-source").modal("show");
      },
      success: function (data) {
        $("#modal-source .modal-content").html(data.html_form);
      }
    });
  };



  var saveForm = function () {
    var form = $(this);
    var formData = new FormData(form[0]);
    $.jGrowl.defaults.closer = false;

    $.ajax({
      url: form.attr("action"),
      data: formData,
      type: form.attr("method"),
      dataType: 'json',
      contentType: false,
      processData: false,
      params: {
                'csrf_token': '{{ csrf_token }}',
                'csrf_name': 'csrfmiddlewaretoken',
                'csrf_xname': 'X-CSRFToken',
              },
      success: function (data) {
        if (data.form_is_valid) {
          $("#source_table tbody").html(data.html_source_list);
          $("#modal-source").modal("hide");
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
          $("#modal-source .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };



  // Create source
  $(".js-add-source").click(loadForm);
  $("#modal-source").on("submit", ".js-source-create-form", saveForm);

  // Update source
  $("#source_table").on("click", ".js-edit-source", loadForm);
  $("#modal-source").on("submit", ".js-source-edit-form", saveForm);

  // Delete source
  $("#source_table").on("click", ".js-delete-source", loadForm);
  $("#modal-source").on("submit", ".js-source-delete-form", saveForm);

});
