//
//
//

$("table#manage_user_table").DataTable({
  "columnDefs": [
    { targets: 'no-sort', orderable: false },
  ],
  paging: false
});

$(".no-sort").removeClass("sorting_asc");

//
//
//

function show_adduser_modal(){
    $("#AddUserModalForm").modal("show");
}

//
//
//

function delete_selected_users(){
  formdata = $("form#manage_users_form").serialize();
  console.log(formdata);


  var anyBoxesChecked = false;
  $(".checkbox_one").each(function() {
      if ($(this).is(":checked")) {
          anyBoxesChecked = true;
      }
  });

  if (anyBoxesChecked == false) {
    alert('Please select at least one checkbox');
    return false;
  }else{
    var url = $(location).attr('href').replace($(location).attr('pathname'), "")+"/admin/delete_selected_users/";

    $.post(url, formdata, function(data){
      location.reload();
    });
  }
}



//***********************************************************************
// Reset Password
//***********************************************************************
//

function reset_password(id){
	$.get("/reset_password/"+id+"/", function(data){
		console.log(data);

		$("#reset_password").modal('show');
		$("#reset_password_data").empty().text(data);
	});
}
