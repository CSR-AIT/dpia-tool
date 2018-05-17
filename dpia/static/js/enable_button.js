// JS to enable the submit button only after at least one checkbox is checked
var checkBoxes = $('tbody .myCheckBox');
checkBoxes.change(function () {
    $('#confirmButton').prop('disabled', checkBoxes.filter(':checked').length < 1);
});

// checkBoxes.change();



$('.file_field').on('keydown keyup change', function(){
  if($(this).val() == ''){
      $('#submit').attr('disabled', 'disabled');
  }else{
      $('#submit').removeAttr('disabled');

      $('.loading_button').on('click', function() {
        var $this = $(this);
        $this.button('loading');
        // setTimeout(function() {
        //   $this.button('reset');
        // }, 10000);
      });
  }
}).trigger('change')
