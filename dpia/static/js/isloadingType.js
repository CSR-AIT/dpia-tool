$(function() {
  // Action on Click
  $( "#load-overlay .btn" ).click(function() {
      $.isLoading({ text: "Loading" });
      // Re-enabling event
      setTimeout( function(){
          $.isLoading( "hide" );
          $( "#load-overlay #message_success" ).html( "PDF Downloaded" )
                                      .addClass("alert alert-success fade in center");
          setTimeout(function(){
            $('#load-overlay #message_success').remove();
          }, 2000);

      }, 2000 );

  });
});
