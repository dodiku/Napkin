

$(".post").click(function(){
  var postID = $(this).children().attr('id');
  // console.log("the clicked postID is: " + postID);

  var url = "/click/" + postID ;

  $.ajax({
    url: url,
    type: 'GET',
    error: function(err){
      console.log("Could not talk to Django");
      console.log(err);
    },
    success: function(data){
      // console.log(data);
    },

  });

});
