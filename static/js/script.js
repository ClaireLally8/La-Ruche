
  $(window).on('load', function() {
        $('#myModal').modal('show');
        
         var p = $('.smart-timeline').html()
    $(".smart-form-timeline").append(p)
   $('#Modal').modal('show');
    });

 $( "#target" ).click(function() {
  setTimeout(function(){ location.reload() }, 3000);
});

$(document).ready(function() {

     // set an element
     $("#today").val( moment().format('DD-MM-YYYY') );

    
});

