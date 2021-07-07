
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
 $( ".patient-row" ).click(function() {
     $(".patient-row").removeClass("zoom");
     $(".editimg").addClass('hidden');
    $(this).addClass("zoom");
    $(".editimg",this).removeClass('hidden');
   
});