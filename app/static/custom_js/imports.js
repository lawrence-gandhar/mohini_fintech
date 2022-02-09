$(document).ready(function(){

  console.log(1);

  $(".nav-tabs a").removeClass("active");
  $(".tab-pane").removeClass("active");

  if(status == 1){
    $("#tab_master").addClass("active");
  }
  if(status == 2){
    $("#tab_pd").addClass("active");
  }
  if(status == 3){
    $("#tab_lgd").addClass("active");
  }
  if(status == 4){
    $("#tab_stage").addClass("active");
  }
  if(status == 5){
    $("#tab_eir").addClass("active");
  }
  if(status == 6){
    $("#tab_ecl").addClass("active");
  }
  if(status == 7){
    $("#tab_ead").addClass("active");
  }
  if(status == 8){
    $("#tab_product").addClass("active");
  }
  if(status == 9){
    $("#tab_collateral").addClass("active");
  }
});



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
function delete_selected_records(){
  var r = confirm("Do you really want to delete the selected records?");
  if (r == true) {
    if($(".checkbox_one:checked").length > 0){
      formdata = $("#move_all_to_final").serialize();
      $.post(delete_selected_url, formdata, function(data){
        location.reload();
      });
    }else{
      var r1 = confirm("No records are selected. Do you want to continue? This will delete all the records");
      if (r1 == true) {
        $.get(delete_selected_url, function(data){
          location.reload();
        });
      }
    }
  }
}

//
//
//

function delete_final_selected_records(){

  var r = confirm("Do you really want to delete the selected records?");
  if (r == true) {

    if($(".checkbox_one:checked").length > 0){
      formdata = $("#move_all_to_final").serialize();
      $.post(delete_selected_url, formdata, function(data){
        location.reload();
      });
    }else{
      if($("#report_start_date").val().trim() !=""){
        if($("#report_end_date").val().trim()!=""){

          //
          //

          var start_date = Date.parse($("#report_start_date").val().trim());
          var end_date = Date.parse($("#report_end_date").val().trim());

          if(start_date<=end_date){
            var r1 = confirm("Start & End Dates are selected. Do you want to continue? This will delete all the records");
            if (r1 == true) {
              formdata = $("#run_report_form").serialize();
              $.post(delete_selected_url, formdata, function(data){
                location.reload();
              });
            }
          }else{
            alert("Invalid Dates selected");
            return false;
          }

          //
          //
        }else{
          alert("Start & End Dates are required for delete operation");
        }
      }else{
        if($("#report_end_date").val().trim()!="" && $("#report_start_date").val().trim() ==""){
            alert("Start & End Dates are required for delete operation");
        }else{
          var r1 = confirm("No records are selected. Do you want to continue? This will delete all the records");
          if (r1 == true) {
            $.get(delete_selected_url, function(data){
              location.reload();
            });
          }
        }
      }
    }
  }
}

//
//
//


function delete_report_selected_records(){

  var r = confirm("Do you really want to delete the selected records?");
  if (r == true) {

    if($(".checkbox_one:checked").length > 0){
      formdata = $("#search_download_form").serialize();
      $.post(delete_selected_url, formdata, function(data){
        location.reload();
      });
    }else{
      if($("#report_start_date").val().trim() !=""){
        if($("#report_end_date").val().trim()!=""){

          //
          //

          var start_date = Date.parse($("#report_start_date").val().trim());
          var end_date = Date.parse($("#report_end_date").val().trim());

          if(start_date<=end_date){
            var r1 = confirm("Start & End Dates are selected. Do you want to continue? This will delete all the records");
            if (r1 == true) {
              formdata = $("#search_download_form").serialize();
              $.post(delete_selected_url, formdata, function(data){
                location.reload();
              });
            }
          }else{
            alert("Invalid Dates selected");
            return false;
          }

          //
          //
        }else{
          alert("Start & End Dates are required for delete operation");
        }
      }else{
        if($("#report_end_date").val().trim()!="" && $("#report_start_date").val().trim() ==""){
            alert("Start & End Dates are required for delete operation");
        }else{
          var r1 = confirm("No records are selected. Do you want to continue? This will delete all the records");
          if (r1 == true) {
            $.get(delete_selected_url, function(data){
              location.reload();
            });
          }
        }
      }
    }
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

  if(status == 1){
    $("#edit_cin").val(jsdata[id]["cin"]);
    $("#edit_account_no").val(jsdata[id]["account_no"]);

    if(jsdata[id]["account_status"]) $("#edit_account_status").val(1);
    else $("#edit_account_status").val(0);

    $("#edit_account_type").val(jsdata[id]["account_type"]);
    $("#edit_sectors").val(jsdata[id]["sectors"]);
    $("#edit_customer_name").val(jsdata[id]["customer_name"]);
    $("#edit_contact_no").val(jsdata[id]["contact_no"]);
    $("#edit_email").val(jsdata[id]["email"]);
    $("#edit_pan").val(jsdata[id]["pan"]);
    $("#edit_aadhar_no").val(jsdata[id]["aadhar_no"]);
    $("#edit_customer_addr").val(jsdata[id]["customer_addr"]);
    $("#edit_pin").val(jsdata[id]["pin"]);
  }

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

  if(status == 4){
    $("#edit_old_rating").val(jsdata[id]["old_rating"]);
    $("#edit_new_rating").val(jsdata[id]["new_rating"]);
    $("#edit_rating_3").val(jsdata[id]["rating_3"]);
    $("#edit_rating_4").val(jsdata[id]["rating_4"]);
    $("#edit_rating_5").val(jsdata[id]["rating_5"]);
    $("#edit_rating_6").val(jsdata[id]["rating_6"]);
    $("#edit_rating_7").val(jsdata[id]["rating_7"]);
    $("#edit_day_bucket_1").val(jsdata[id]["day_bucket_1"]);
    $("#edit_day_bucket_2").val(jsdata[id]["day_bucket_2"]);
    $("#edit_day_bucket_3").val(jsdata[id]["day_bucket_3"]);
    $("#edit_day_bucket_4").val(jsdata[id]["day_bucket_4"]);
    $("#edit_day_bucket_5").val(jsdata[id]["day_bucket_5"]);
    $("#edit_day_bucket_6").val(jsdata[id]["day_bucket_6"]);
    $("#edit_day_bucket_7").val(jsdata[id]["day_bucket_7"]);
    $("#edit_day_bucket_8").val(jsdata[id]["day_bucket_8"]);
    $("#edit_day_bucket_9").val(jsdata[id]["day_bucket_9"]);
    $("#edit_day_bucket_10").val(jsdata[id]["day_bucket_10"]);
    $("#edit_day_bucket_11").val(jsdata[id]["day_bucket_11"]);
    $("#edit_day_bucket_12").val(jsdata[id]["day_bucket_12"]);
    $("#edit_day_bucket_13").val(jsdata[id]["day_bucket_13"]);
    $("#edit_day_bucket_14").val(jsdata[id]["day_bucket_14"]);
    $("#edit_day_bucket_15").val(jsdata[id]["day_bucket_15"]);
    $("#edit_criteria").val(jsdata[id]["criteria"]);
    $("#edit_cooling_period_1").val(jsdata[id]["cooling_period_1"]);
    $("#edit_cooling_period_2").val(jsdata[id]["cooling_period_2"]);
    $("#edit_cooling_period_3").val(jsdata[id]["cooling_period_3"]);
    $("#edit_cooling_period_4").val(jsdata[id]["cooling_period_4"]);
    $("#edit_cooling_period_5").val(jsdata[id]["cooling_period_5"]);
    $("#edit_rbi_window").val(jsdata[id]["rbi_window"]);
    $("#edit_mgmt_overlay_1").val(jsdata[id]["mgmt_overlay_1"]);
    $("#edit_mgmt_overlay_2").val(jsdata[id]["mgmt_overlay_2"]);
  }

  if(status == 5){
    $("#edit_period").val(jsdata[id]["period"]);
    $("#edit_loan_availed").val(jsdata[id]["loan_availed"]);
    $("#edit_cost_avail").val(jsdata[id]["cost_avail"]);
    $("#edit_rate").val(jsdata[id]["rate"]);
    $("#edit_emi").val(jsdata[id]["emi"]);
    $("#edit_os_principal").val(jsdata[id]["os_principal"]);
    $("#edit_os_interest").val(jsdata[id]["os_interest"]);
    $("#edit_fair_value").val(jsdata[id]["fair_value"]);
    $("#edit_coupon").val(jsdata[id]["coupon"]);
    $("#edit_discount_factor").val(jsdata[id]["discount_factor"]);
    $("#edit_col_1").val(jsdata[id]["col_1"]);
    $("#edit_col_2").val(jsdata[id]["col_2"]);
    $("#edit_col_3").val(jsdata[id]["col_3"]);
    $("#edit_default_eir").val(jsdata[id]["default_eir"]);
    $("#edit_cop_tagged").val(jsdata[id]["cop_tagged"]);
  }

  if(status == 6){
    $("#edit_tenure").val(jsdata[id]["tenure"]);
    console.log(jsdata)
  }

  if(status == 7){
    $("#edit_outstanding_amount").val(jsdata[id]["outstanding_amount"]);
    $("#edit_undrawn_upto_1_yr").val(jsdata[id]["undrawn_upto_1_yr"]);
    $("#edit_undrawn_greater_than_1_yr").val(jsdata[id]["undrawn_greater_than_1_yr"]);
    $("#edit_collateral_1_value").val(jsdata[id]["collateral_1_value"]);
    $("#edit_collateral_1_rating").val(jsdata[id]["collateral_1_rating"]);
    $("#edit_collateral_1_residual_maturity").val(jsdata[id]["collateral_1_residual_maturity"]);
    $("#edit_collateral_2_value").val(jsdata[id]["collateral_2_value"]);
    $("#edit_collateral_2_rating").val(jsdata[id]["collateral_2_rating"]);
    $("#edit_collateral_2_residual_maturity").val(jsdata[id]["collateral_2_residual_maturity"]);
  }

  if(status == 8){
    $("#edit_product_name").val(jsdata[id]["product_name"]);
    $("#edit_product_code").val(jsdata[id]["product_code"]);
    $("#edit_product_catgory").val(jsdata[id]["product_catgory"]);
    $("#edit_basel_product").val(jsdata[id]["basel_product"]);
    $("#edit_basel_product_code").val(jsdata[id]["basel_product_code"]);
    $("#edit_drawn_cff").val(jsdata[id]["drawn_cff"]);
    $("#edit_cff_upto_1_yr").val(jsdata[id]["cff_upto_1_yr"]);
    $("#edit_cff_gt_1_yr").val(jsdata[id]["cff_gt_1_yr"]);
  }

  if(status == 9){
    $("#edit_product_name").val(jsdata[id]["product_name"]);
    $("#edit_collateral_code").val(jsdata[id]["collateral_code"]);
    $("#edit_collateral_type").val(jsdata[id]["collateral_type"]);
    $("#edit_issuer_type").val(jsdata[id]["issuer_type"]);
    $("#edit_collateral_eligibity").val(jsdata[id]["collateral_eligibity"]);
    $("#edit_rating_available").val(jsdata[id]["rating_available"]);
    $("#edit_collateral_rating").val(jsdata[id]["collateral_rating"]);
    $("#edit_residual_maturity").val(jsdata[id]["residual_maturity"]);
    $("#edit_basel_collateral_type").val(jsdata[id]["basel_collateral_type"]);
    $("#edit_basel_collateral_subtype").val(jsdata[id]["basel_collateral_subtype"]);
    $("#edit_basel_collateral_code").val(jsdata[id]["basel_collateral_code"]);
    $("#edit_basel_collateral_rating").val(jsdata[id]["basel_collateral_rating"]);
    $("#edit_soverign_issuer").val(jsdata[id]["soverign_issuer"]);
    $("#edit_other_issuer").val(jsdata[id]["other_issuer"]);
  }

}

//
/////
//
function move_data_bg_process(){
  //$("#moving_data_main_div").empty();

  html = '<div id="moving_data_inner_div" class="alert bg-blue-alert d-flex align-items-center fade show" role="alert" style="margin-bottom: 20px;">';
  html += '</div>';
  $("#moving_data_main_div").empty().append(html);
  $("#moving_data_inner_div").empty().text("Please wait. Process is in progress");


  setTimeout(function(){
    $.get(bg_data_url, function(data){
      if(data.ret == false){
        $("#moving_data_inner_div").removeClass("bg-blue-alert").addClass("bg-red-alert");

        html = '<table class="table borderless text-white" style="font-size:85%; margin-bottom:0px;">';
        html += '<tr><td colspan="2"><strong>'+data.msg+'</strong></td></tr>';
        html += '<tr><td style="width: 200px;border-style:none; padding: 5px 10px 0px 10px;">Total Records</td><td style="border-style:none; padding: 5px 10px 0px 10px;">: '+data.total_records+'</td></tr>';
        html += '<tr><td style="width: 140px;border-style:none; padding: 0px 10px;">Valid Records</td><td style="border-style:none; padding: 0px 10px;">: '+data.records_valid+'</td></tr>';
        html += '<tr><td style="width: 140px;border-style:none; padding: 0px 10px;">Valid Records Moved</td><td style="border-style:none; padding: 0px 10px;">: '+data.no_of_records_moved+'</td></tr>';
        html += '<tr><td style="width: 140px;border-style:none; padding: 0px 10px;">Valid Records Failed</td><td style="border-style:none; padding: 0px 10px;">: '+data.no_of_records_failed+'</td></tr>';
        html += '<tr><td colspan="2">Please Wait.. Cleaning data may take couple of seconds</td></tr>';
        html += '</table>';
      }else{
        $("#moving_data_inner_div").removeClass("bg-blue-alert").addClass("bg-green-alert");

        html = '<table class="table borderless text-white" style="font-size:85%; margin-bottom:0px;">';
        html += '<tr><td colspan="2"><strong>'+data.msg+'</strong></td></tr>';
        html += '<tr><td style="width: 200px;border-style:none; padding: 5px 10px 0px 10px;">Total Records</td><td style="border-style:none; padding: 5px 10px 0px 10px;">: '+data.total_records+'</td></tr>';
        html += '<tr><td style="width: 140px;border-style:none; padding: 0px 10px;">Valid Records</td><td style="border-style:none; padding: 0px 10px;">: '+data.records_valid+'</td></tr>';
        html += '<tr><td style="width: 140px;border-style:none; padding: 0px 10px;">Valid Records Moved</td><td style="border-style:none; padding: 0px 10px;">: '+data.no_of_records_moved+'</td></tr>';
        html += '<tr><td style="width: 140px;border-style:none; padding: 0px 10px;">Valid Records Failed</td><td style="border-style:none; padding: 0px 10px;">: '+data.no_of_records_failed+'</td></tr>';
        html += '<tr><td colspan="2">Please Wait.. Cleaning data may take couple of seconds</td></tr>';
        html += '</table>';
      }
      $("#moving_data_inner_div").empty().append(html);

      setTimeout(function(){location.reload();}, 4000);
    });


  }, 2000);
}

//
//
//

function run_report(){

  var account_no = $("#report_account_no").val();

  if(typeof account_no == 'undefined'){
    account_no = "";
  }


  var start_date = $("#report_start_date").val();
  var end_date = $("#report_end_date").val();

  if(account_no.trim() !="" || start_date.trim() !="" || end_date.trim() !=""){
    $("form#run_report_form").prop("method", "post").submit();
  }else{
    if($('.checkbox_one:checked').length >= 1){
      $("form#move_all_to_final").prop("method", "post").submit();
    }else{
      $("form#run_report_form").prop("method", "post").submit();
    }
  }

}

//
//
//

function run_search(){

  console.log("start");

  var account_no = $("#report_account_no").val();

  if(typeof account_no == 'undefined'){
    account_no = "";
  }

  var start_date = $("#report_start_date").val();
  var end_date = $("#report_end_date").val();

  if(account_no.trim() !="" || start_date.trim() !="" || end_date.trim() !=""){
    $("form#run_report_form").prop("action", location.href).prop("method", "get").submit();

  }else{
    if($('.checkbox_one:checked').length >= 1){
      $("form#run_report_form").prop("action", location.href).submit();
    }else{
      $("form#run_report_form").prop("action", location.href).submit();
    }
  }

}
