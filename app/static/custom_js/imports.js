$(document).ready(function(){

  $(".nav-tabs a").removeClass("active");
  $(".tab-pane").removeClass("active");

  if(status == 1){
    $("#tab_master").addClass("active");
  }
  if(status == 2){
    $("#tab_pd").addClass("active");
  }
  else if(status == 3){
    $("#tab_lgd").addClass("active");
  }
  else if(status == 4){
    $("#tab_stage").addClass("active");
  }
  else if(status == 5){
    $("#tab_eir").addClass("active");
  }
  else if(status == 6){
    $("#tab_ecl").addClass("active");
  }
});

console.log("error");
console.log(status);

//
//
//
function delete_single_record(elem){
  var r = confirm("Do you really want to delete this record?");
  if (r == true) {
    location.href = $(elem).attr("params");
  }
}

//
//
//
function confirm_row_move(elem){
  var r = confirm("Do you really want to confirm and move this record?");
  if (r == true) {
    location.href = $(elem).attr("params");
  }
}

//
//
//
function load_edit_data(id){
  $("#EditModal").modal("show");

  if(jsdata[id]["account_no_id"] !=null){
    $("#edit_account_no").val(jsdata[id]["account_no_id_related"]);
  }else{
    if(jsdata[id]["account_no_temp"] !=""){
      $("#edit_account_no").val(jsdata[id]["account_no_temp"]);
    }
  }

  $("#edit_id").val(id);
  $("#edit_date").val(jsdata[id]["date"]);

  if(status == 2){
    $("#edit_default_col").val(jsdata[id]["default_col"]);
    $("#edit_factor_1").val(jsdata[id]["factor_1"]);
    $("#edit_factor_2").val(jsdata[id]["factor_2"]);
    $("#edit_factor_3").val(jsdata[id]["factor_3"]);
    $("#edit_factor_4").val(jsdata[id]["factor_4"]);
    $("#edit_factor_5").val(jsdata[id]["factor_5"]);
    $("#edit_factor_6").val(jsdata[id]["factor_6"]);
    $("#edit_mgmt_overlay_1").val(jsdata[id]["mgmt_overlay_1"]);
    $("#edit_mgmt_overlay_2").val(jsdata[id]["mgmt_overlay_2"]);
  }

  if(status == 3){
    $("#edit_ead_os").val(jsdata[id]["ead_os"]);
    $("#edit_pv_cashflows").val(jsdata[id]["pv_cashflows"]);
    $("#edit_pv_cost").val(jsdata[id]["pv_cost"]);
    $("#edit_beta_value").val(jsdata[id]["beta_value"]);
    $("#edit_sec_flag").val(jsdata[id]["sec_flag"]);
    $("#edit_factor_4").val(jsdata[id]["factor_4"]);
    $("#edit_factor_5").val(jsdata[id]["factor_5"]);
    $("#edit_avg_1").val(jsdata[id]["avg_1"]);
    $("#edit_avg_2").val(jsdata[id]["avg_2"]);
    $("#edit_avg_3").val(jsdata[id]["avg_3"]);
    $("#edit_avg_4").val(jsdata[id]["avg_4"]);
    $("#edit_avg_5").val(jsdata[id]["avg_5"]);
    $("#edit_mgmt_overlay_1").val(jsdata[id]["mgmt_overlay_1"]);
    $("#edit_mgmt_overlay_2").val(jsdata[id]["mgmt_overlay_2"]);
  }
}

//
/////
//
function move_data_bg_process(){
  $.get(bg_data_url, function(data){
    console.log(data);
  });
}




console.log("dkhsk error");
