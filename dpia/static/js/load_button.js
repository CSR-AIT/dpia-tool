// Show "Loading..." button
// $('.loading_button').on('click', function() {
//   var $this = $(this);
//   $this.button('loading');
//   var startTime = (new Date()).getTime();
//   $(window).load(function () {
//     var endTime = (new Date()).getTime();
//     var millisecondsLoading = endTime - startTime;
//     setTimeout(function() {
//       $this.button('reset');
//     }, millisecondsLoading);
//   });
// });

// var loadTime = window.performance.timing.domContentLoadedEventEnd-window.performance.timing.navigationStart;

// Show "Loading..." button
$('.loading_button').on('click', function() {
  var $this = $(this);
  var loadTime = window.performance.timing.domContentLoadedEventEnd-window.performance.timing.navigationStart;
  $this.button('loading');
  // setTimeout(function() {
  //   $this.button('reset');
  // }, 10000);
});

// jQuery(window).load(function(){
//     jQuery('loading_button').fadeOut();
//   });
