
  $(window).on('load', function() {
        $('#myModal').modal('show');
    });

 $( "#target" ).click(function() {
  setTimeout(function(){ location.reload() }, 3000);
});