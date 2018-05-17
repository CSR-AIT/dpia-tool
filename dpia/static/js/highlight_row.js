// hightlight row when checkbox is checked
$(":checkbox").change(function() {
  $(this).closest("tr").toggleClass("highlight", this.checked);
});
