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

//
// EDIT USER FORM DATA LOAD
//
function load_edit_data(id){
  $("#edit_id").val(id);

  $.each(users_json, function(i,v){
    if(v["id"] == id){
      $("#edit_username").val(v["username"]);
      $("#edit_email").val(v["email"]);
      $("#edit_first_name").val(v["first_name"]);
      $("#edit_last_name").val(v["last_name"]);

      if(v["is_superuser"]){
        $("#edit_is_superuser").prop("checked",true);
      }else{
        $("#edit_is_superuser").prop("checked",false);
      }

      if(v["is_staff"]){
        $("#edit_is_staff").prop("checked",true);
      }else{
        $("#edit_is_staff").prop("checked",false);
      }

      $("#EditUserModalForm").modal("show");
      return true;
    }
  });
  return false;
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
