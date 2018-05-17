$(function () {


  /* Functions */

  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-q").modal("show");

      },
      success: function (data) {
        $("#modal-q .modal-content").html(data.html_form);
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
          $("#q_table tbody").html(data.html_q_list);
          $("#modal-q").modal("hide");
          $.each(data.messages, function (i, m) {
            $.jGrowl(m.message, {
              position: 'top-right',
              sticky: false,
              theme: 'success',
              // header: '<i class=fa fa-fw>&#xf058;</i> Success',
              life: 5000,
              openDuration: 'fast',
              // closeDuration: 'fast',
            });
          });


          // var q_description = data.q_description;
          // $('.inner_success').append('<i class=fa>&#xf058;</i> Questionnaire ' + '"' + q_description + '"' + ' was changed successfully. <br>');
        }
        else {
          $("#modal-q .modal-content").html(data.html_form);
          $.jGrowl("Please fill out the fields or check a box.", {
            position: 'top-right',
            sticky: false,
            theme: 'danger',
            // header: '<i class=fa fa-fw>&#xf06a;</i> Error',
            life: 5000,
            openDuration: 'fast',
          });
        }
      }
    });
    return false;
  };



  var saveSgamForm = function () {
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
          $("#q_table tbody").html(data.html_q_list);
          $("#modal-q").modal("hide");

          $.each(data.messages, function (i, m) {
            $.jGrowl(m.message, {
              position: 'top-right',
              sticky: false,
              openDuration: 'fast',
              theme: 'success',
              // header: '<i class=fa fa-fw>&#xf058;</i> Success',
            });
          });

          $('#hidden_link').css('display', 'inline');

        }
        else {
          $("#modal-q .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };



  // Call functions
  $(".js-add").click(loadForm);
  $("#modal-q").on("submit", ".js-add-form", saveForm);

  $(".js-add-sgam").click(loadForm);
  $("#modal-q").on("submit", ".js-sgam-add-form", saveSgamForm);

  $("#q_table").on("click", ".js-edit", loadForm);
  $("#modal-q").on("submit", ".js-edit-form", saveForm);

  $("#q_table").on("click", ".js-delete", loadForm);
  $("#modal-q").on("submit", ".js-delete-form", saveForm);


  // only for pre-assessment
  var loadPreForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-q").modal("show");
      },
       success: function (data) {
        $("#modal-q .modal-content").html(data.html_form);
      }
    });
  };

  $(".js-confirm-pre-assessment").click(loadPreForm);
  $("#modal-q").on("submit", ".js-confirm-pre-assessment-form", saveForm);
});
