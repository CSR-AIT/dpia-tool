$(function () {
    $('.add-row').click(function() {
      return addForm(this, 'form');
    });
    $('.delete-row').click(function() {
      return deleteForm(this, 'form');
    })
})
