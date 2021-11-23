$(document).ready(function(){});

//
//
//

function ask_confirm(func){
  var result = confirm("Are you sure to delete?");
  if(result){
      let xx = func();
  }
}

//
//
//

function user(){
  console.log("user")
}
