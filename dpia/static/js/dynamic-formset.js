	function updateElementIndex(el, prefix, ndx) {
		var id_regex = new RegExp('(' + prefix + '-\\d+)');
		var replacement = prefix + '-' + ndx;
		if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
		if (el.id) el.id = el.id.replace(id_regex, replacement);
		if (el.name) el.name = el.name.replace(id_regex, replacement);
	}

  function addForm(btn, prefix) {
    var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    var row = $('.dynamic-form:last').clone(true).get(0);
    $(row).removeAttr('id').insertAfter($('.dynamic-form:last')).children('.hidden').removeClass('hidden');

    $(row).children().not(':last').children().each(function() {
	    updateElementIndex(this, prefix, formCount);
	    $(this).val('');
    });

		// Hide specific columns when a new process is added
		$('.dynamic-form:last').addClass('hide_column');
		$('.hide_column td:first').html(''); // Hide first column-td for the newly added process forms
		// $('.hide_column td').eq(4).html('');
		$('.hide_column td').eq(5).html(''); // Hide the 5th column for the newly added process forms

    $(row).find('.delete-row').click(function() {
	    deleteForm(this, prefix);
    });
    $('#id_' + prefix + '-TOTAL_FORMS').val(formCount + 1);
    return false;
  }

  function deleteForm(btn, prefix) {
    $(btn).parents('.dynamic-form').remove();
    var forms = $('.dynamic-form');
    $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
    for (var i=0, formCount=forms.length; i<formCount; i++) {
	    $(forms.get(i)).children().not(':last').children().each(function() {
	        updateElementIndex(this, prefix, i);
	    });
    }
    return false;
  }
