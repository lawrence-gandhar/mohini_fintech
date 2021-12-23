#
# AUTHOR : LAWRENCE GANDHAR
# Project For Mohini - (India)
# Project Date : 14th Sept 2021
#

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages

from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ObjectDoesNotExist

from django.utils import timezone

from django.views.decorators.csrf import csrf_exempt

from django.db import IntegrityError
from django.db import connection
from django.db.models import F, Count, expressions, Q

from . forms import CreateUserForm, EditUserForm
from . import helpers
from . import constants
from . import background_tasks
from . models import *

import io
import csv
import calendar
import time
import json
from collections import defaultdict, Counter
import os




#**********************************************************************
# ENDPOINT: DASHBOARD - ADMIN
#**********************************************************************
def dashboard(request):
    data = defaultdict()
    data["sidebar_active"] = 1
    data["content_template"] = "administrator/dashboard.html"
    return render(request, "administrator/index.html", data)


#**********************************************************************
# ENDPOINT: MANAGE USERS
#**********************************************************************
def manage_users(request):

    data = defaultdict()
    data["content_template"] = "administrator/manage_users.html"
    data["js_files"] = ['custom_js/admin.js']
    data["add_user_form"] = CreateUserForm()
    data["edit_user_form"] = EditUserForm(auto_id = "edit_%s")

    data["model_show"] = False
    data["sidebar_active"] = 2

    data["users"] = User.objects.all().values('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    data["users_json"] = json.dumps(list(data["users"]), cls=DjangoJSONEncoder)

    if request.POST:
        data["add_user_form"] = CreateUserForm(request.POST)

        if data["add_user_form"].is_valid():
            data["model_show"] = False
            data["add_user_form"].save()
            messages.success(request, "User Added Successfully")
            return redirect("manage_users")
        else:
            data["model_show"] = True
            errors = helpers.user_creation_form_errors(data["add_user_form"].errors)
            messages.error(request, helpers.format_errors(errors))

    return render(request, "administrator/index.html", data)


#**********************************************************************
# ENDPOINT: DELETE USER
#**********************************************************************
def delete_user(request, ins=None):
    if ins is not None:
        try:
            User.objects.get(pk=ins).delete()
            messages.success(request, "User Deleted Successfully")
        except ObjectDoesNotExist:
            messages.error(request, "Delete Operation Failed")
    else:
        messages.error(request, "Delete Operation Failed")
    return redirect("manage_users")


#**********************************************************************
# ENDPOINT: DELETE SELECTED USERS
#**********************************************************************
def delete_selected_users(request):
    if request.POST:
        checkbox_one = request.POST.getlist('checkbox_one', None)

        if checkbox_one is not None:
            ids = [int(x) for x in checkbox_one]
            User.objects.filter(pk__in = ids).delete()
    return HttpResponse("0")


#**********************************************************************
# ENDPOINT: EDIT USER
#**********************************************************************
def edit_user(request):
    if request.POST:
        try:
            id = User.objects.get(pk = int(request.POST["id"]))
        except ObjectDoesNotExist:
            messages.error(request, "Invalid Operation")

        form = EditUserForm(request.POST, instance = id)
        if form.is_valid():
            form.save()
            messages.success(request, "Record Edited Successfully")
        else:
            errors = helpers.user_creation_form_errors(form.errors)
            messages.error(request, helpers.format_errors(errors))
    return redirect("manage_users")


#**********************************************************************
# ENDPOINT: MANAGE NEW USER
#**********************************************************************
def manage_new_users(request):
    data = defaultdict()
    data["content_template"] = "administrator/manage_new_users.html"
    data["js_files"] = []

    data["sidebar_active"] = 2

    data["users"] = New_User.objects.all().values('id', 'email', 'first_name', 'last_name', 'created_on', 'email_sent_on')

    return render(request, "administrator/index.html", data)


#**********************************************************************
# ENDPOINT: ACCEPT NEW USER
#**********************************************************************
def accept_new_users(request, ids=None):

    if request.POST:
        ids = request.POST.getlist("checkbox_one",None)
        error_found = False
        error_count = 0

        if len(ids) > 0:
            users = New_User.objects.filter(pk__in = ids)
        else:
            users = New_User.objects.all()

        if not users.exists():
            messages.error(request, "No Records were found")
            return redirect("manage_new_users")

        #
        # Process only if records are found
        for user in users:
            passwd = User.objects.make_random_password()

            try:
                ins = User.objects.create(
                    email = user.email,
                    username = user.email,
                    password = make_password(passwd),
                    first_name = user.first_name,
                    last_name = user.last_name
                )

                users.delete()
            except IntegrityError:
                error_found = True
                error_count += 1

        if error_found:
            if error_count < len(users):
                messages.success(request, "{} records cannot be moved because email address is already present in registered users list".format(error_count))
            else:
                messages.error(request, "No Records were added to the registered users list")
        else:
            messages.success(request, "Users Added to registered users list")

    else:
        if ids is not None:
            try:
                user = New_User.objects.get(pk = int(ids))
            except:
                messages.error(request, "Unknown Error Occurred!")
                return redirect("manage_new_users")

            #
            # Process if no error
            passwd = User.objects.make_random_password()

            try:
                ins = User.objects.create(
                    email = user.email,
                    username = user.email,
                    password = make_password(passwd),
                    first_name = user.first_name,
                    last_name = user.last_name
                )

                user.delete()

                messages.success(request, "User Added to registered users list")

                helpers.send_email_accept_user(ins, passwd)

            except IntegrityError:
                messages.error(request, "Record cannot be moved because email address is already present in registered users list")
        else:
            messages.error(request, "Unknown Error Occurred!")
    return redirect("manage_new_users")


#**********************************************************************
# ENDPOINT: REJECT NEW USERS
#**********************************************************************
def reject_new_users(request, ids=None):

    if request.POST:
        ids = request.POST.getlist("ids",None)
        error_found = False
        error_count = 0

        if len(ids) > 0:
            users = New_User.objects.filter(pk__in = ids)
        else:
            users = New_User.objects.all()

        if not users.exists():
            messages.error(request, "No Records were found")
            return redirect("manage_new_users")

        #
        # Process if records found
        for user in users:
            user.status =  1
            user.save()
    else:
        if ids is not None:
            try:
                user = New_User.objects.get(pk = int(ids))
                user.status = 1
                user.save()
            except:
                pass
        else:
            messages.error(request, "Unknown Error Occurred!")
    return redirect("manage_new_users")


#**********************************************************************
# ENDPOINT: DELETE NEW USERS
#**********************************************************************
def delete_new_users(request, ids=None):

    if request.POST:
        ids = request.POST.getlist("ids",None)
        error_found = False
        error_count = 0

        if len(ids) > 0:
            users = New_User.objects.filter(pk__in = ids)
        else:
            users = New_User.objects.all()

        if not users.exists():
            messages.error(request, "No Records were found")
            return redirect("manage_new_users")
        else:
            users.delete()
            messages.success(request, "Records deleted successfully")
    else:
        if ids is not None:
            try:
                New_User.objects.get(pk = int(ids)).delete()
            except:
                pass
        else:
            messages.error(request, "Unknown Error Occurred!")
    return redirect("manage_new_users")


#**********************************************************************
# ENDPOINT: MANAGE IMPORTS
#**********************************************************************
def manage_imports(request, tab_status=None):
    data = defaultdict()

    if tab_status is None:
        tab_status = "master"

    data["tab_status"] = tab_status
    data["tab_active"] = constants.TAB_ACTIVE[tab_status][0]
    data["content_template"] = constants.TAB_ACTIVE[tab_status][1]
    data["js_files"] = ['custom_js/imports.js']
    data["sidebar_active"] = 3

    #
    #
    if request.POST:
        data["items_list"] = search_data(constants.TAB_ACTIVE[tab_status][3], request.POST, tab_status)

    else:
        if tab_status not in ["master", "product", "collateral"]:
            data["items_list"] = constants.TAB_ACTIVE[tab_status][3].all().select_related("account_no")
        elif tab_status  == "master":
            data["items_list"] = constants.TAB_ACTIVE[tab_status][3].all().order_by("account_no")
        elif tab_status in ["product", "collateral"]:
            data["items_list"] = constants.TAB_ACTIVE[tab_status][3].all()

    data["items_list_json"] = helpers.queryset_row_to_json(data["items_list"])

    #
    #


    return render(request, "administrator/index.html", data)


#**********************************************************************
# Method to fetch data based on filters
# Can be done on initial and final datasets
# @model_obj: <model_name>.objects
# @form_data: request.POST or request.GET
#**********************************************************************
def search_data(model_obj = None, form_data = None, tab_status = None):

    qry = None

    if model_obj is not None and form_data is not None:

        form_fields = form_data.keys()

        qry = model_obj

        #
        # If Master
        if tab_status == "master":
            if "account_no" in form_fields:
                if form_data["account_no"].strip()!="":
                    acc = [x[0] for x in AccountMaster.objects.filter(
                        Q(account_no__icontains = form_data["account_no"]) |
                        Q(customer_name__icontains = form_data["account_no"])
                    ).values_list("id")]

                    qry = qry.filter(id__in = acc)
        else:

            #
            #
            if tab_status in ("product", "collateral"):
                if "product_name" in form_fields:
                    qry = qry.filter(product_name__icontains = form_data["product_name"])
                if "product_code" in form_fields:
                    qry = qry.filter(product_code__icontains = form_data["product_code"])

                if "collateral_code" in form_fields:
                    qry = qry.filter(Q(collateral_code__icontains = form_data["collateral_code"]) | Q(basel_collateral_code__icontains = form_data["collateral_code"]))
            else:
                #
                # Check & Fetch Account Number Parameter
                if "account_no" in form_fields:
                    if form_data["account_no"].strip()!="":
                        acc_list = [ x.strip() for x in form_data["account_no"].split(",")]

                        for i in acc_list:
                            acc = [x[0] for x in AccountMaster.objects.filter(account_no__icontains = i).values_list("id")]
                            qry = qry.filter(Q(account_no_id__in = acc))



        #
        # Date Range Data Filter
        # Check & Fetch Start Date Input Parameter
        if "start_date" in form_fields:
            if form_data["start_date"].strip()!="":
                qry = qry.filter(date__gte = form_data["start_date"])
                #
                # Check & Fetch End Date Input Parameter
                if "end_date" in form_fields:
                    if form_data["end_date"].strip()!="":
                        qry = qry.filter(date__lte = form_data["end_date"])
            else:
                if "end_date" in form_fields:
                    if form_data["end_date"].strip()!="":
                        qry = qry.filter(date__lte = form_data["end_date"])

        #
        # Edited Records Filter
        if "edited" in form_fields:
            if form_data["edited"].strip()!="":
                qry = qry.filter(edited_by__isnull = False)

        #
        # Is Account Number Missing
        if "acc_missing" in form_fields:
            if form_data["acc_missing"] !="":
                qry = qry.exclude(account_no_temp__isnull = True)

        if tab_status not in ["master", "product", "collateral"]:
            qry = qry.select_related("account_no")
    return qry


#**********************************************************************
# METHOD TO IMPORT DATA FROM UPLOADED FILE
#**********************************************************************
def import_data_from_file(request):
    if request.POST:

        csv_file = request.FILES['formFile']
        import_type = request.POST["import_type"]

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'THIS IS NOT A CSV FILE')
            return redirect("manage_imports", import_type)

        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)

        data_set = csv.DictReader(io_string, delimiter=',', quotechar='"')

        # Get header names
        column_names = data_set.fieldnames

        missing_columns = [x for x in constants.TAB_ACTIVE[import_type][2] if x not in column_names]

        if len(missing_columns) == 0:
            if Counter(column_names) != Counter(constants.TAB_ACTIVE[import_type][2]):
                messages.error(request, "Unable to process the file, please check the column headers")
            else:
                ts = calendar.timegm(time.gmtime())
                row_num, row_failed, total_rows = background_tasks.insert_data(data_set, import_type, ts)
                messages.success(request, "<p>Total Rows : {}</p><p>Inserted/Updated : {}</p><p>Failed : {}</p>".format(total_rows, row_num, row_failed))
        else:
            messages.error(request, "Unable to process the file. Columns Not Found : "+', '.join(missing_columns))

        return redirect("manage_imports", import_type)
    return redirect("manage_imports")



#**********************************************************************
# METHOD TO DELETE DATA INTO RELEVANT MODELS
#**********************************************************************
def delete_record(request, tab_status=None, ins=None):
    try:
        constants.TAB_ACTIVE[tab_status][3].get(pk = int(ins)).delete()
        messages.success(request, "Record Deleted Successfully")
    except:
        messages.error(request, "Operation Failed")

    return redirect("manage_imports", tab_status)


#**********************************************************************
# METHOD SELECTED DELETE DATA INTO RELEVANT MODELS
#**********************************************************************
def delete_selected_records(request, tab_status=None):

    ins_list = request.POST.getlist("checkbox_one", None)

    if len(ins_list) == 0:
        constants.TAB_ACTIVE[tab_status][3].all().delete()
    else:
        constants.TAB_ACTIVE[tab_status][3].filter(pk__in = ins_list).delete()
    messages.success(request, "Records Deleted Successfully")

    return HttpResponse("1")

#**********************************************************************
# METHOD TO EDIT DATA OF RELEVANT MODELS
#**********************************************************************
def edit_record(request, tab_status=None):
    if request.POST:

        #AccountMissing.objects.all().delete()

        ins = int(request.POST["id"])

        #
        #
        try:
            obj = constants.TAB_ACTIVE[tab_status][3].get(pk = ins)
        except ObjectDoesNotExist:
            messages.error(request, "Operation Failed")
            return redirect("manage_imports", tab_status)


        #
        #
        if tab_status not in ["master", "product", "collateral"]:
            try:
                account_ins = AccountMaster.objects.get(account_no = request.POST["account_no"])
                obj.account_no = account_ins
                obj.account_no_temp = None
                AccountMissing.objects.filter(account_no = request.POST["account_no"]).delete()
            except ObjectDoesNotExist:
                obj.account_no = None
                obj.account_no_temp = request.POST["account_no"]
                _, created = AccountMissing.objects.update_or_create(account_no = request.POST["account_no"])


        col_names = constants.TAB_ACTIVE[tab_status][2]

        #
        # BASEL PRODUCT ENTRY
        if tab_status == "master":
            obj.account_no = request.POST["account_no"] if request.POST["account_no"].strip()!="" else None if "account_no" in col_names else None
            obj.cin = request.POST["cin"] if request.POST["cin"].strip()!="" else None if "cin" in col_names else None
            obj.account_type = request.POST["account_type"] if request.POST["account_type"].strip()!="" else None if "account_type" in col_names else None
            obj.account_status = request.POST["account_status"] if request.POST["account_status"].strip()!="" else None if "account_status" in col_names else None
            obj.sectors = request.POST["sectors"] if request.POST["sectors"].strip()!="" else None if "sectors" in col_names else None
            obj.customer_name = request.POST["customer_name"] if request.POST["customer_name"].strip()!="" else None if "customer_name" in col_names else None
            obj.contact_no = request.POST["contact_no"] if request.POST["contact_no"].strip()!="" else None if "contact_no" in col_names else None
            obj.email = request.POST["email"] if request.POST["email"].strip()!="" else None if "email" in col_names else None
            obj.pan = request.POST["pan"] if request.POST["pan"].strip()!="" else None if "pan" in col_names else None
            obj.aadhar_no = request.POST["aadhar_no"] if request.POST["aadhar_no"].strip()!="" else None if "aadhar_no" in col_names else None
            obj.customer_addr = request.POST["customer_addr"] if request.POST["customer_addr"].strip()!="" else None if "customer_addr" in col_names else None
            obj.pin = request.POST["pin"] if request.POST["pin"].strip()!="" else None if "pin" in col_names else None

        #
        # BASEL PRODUCT ENTRY
        if tab_status == "product":
            obj.product_name = request.POST["product_name"] if request.POST["product_name"].strip()!="" else None if "product_name" in col_names else None
            obj.product_code = request.POST["product_code"] if request.POST["product_code"].strip()!="" else None if "product_code" in col_names else None
            obj.product_catgory = request.POST["product_catgory"] if request.POST["product_catgory"].strip()!="" else None if "product_catgory" in col_names else None
            obj.basel_product = request.POST["basel_product"] if request.POST["basel_product"].strip()!="" else None if "basel_product" in col_names else None
            obj.basel_product_code = request.POST["basel_product_code"] if request.POST["basel_product_code"].strip()!="" else None if "basel_product_code" in col_names else None
            obj.drawn_cff = request.POST["drawn_cff"] if request.POST["drawn_cff"].strip()!="" else None if "drawn_cff" in col_names else None
            obj.cff_upto_1_yr = request.POST["cff_upto_1_yr"] if request.POST["cff_upto_1_yr"].strip()!="" else None if "cff_upto_1_yr" in col_names else None
            obj.cff_gt_1_yr = request.POST["cff_gt_1_yr"] if request.POST["cff_gt_1_yr"].strip()!="" else None if "cff_gt_1_yr" in col_names else None


        #
        # BASEL PRODUCT ENTRY
        if tab_status == "collateral":
            obj.collateral_code = request.POST["collateral_code"] if request.POST["collateral_code"].strip()!="" else None if "collateral_code" in col_names else None
            obj.collateral_type = request.POST["collateral_type"] if request.POST["collateral_type"].strip()!="" else None if "collateral_type" in col_names else None
            obj.issuer_type = request.POST["issuer_type"] if request.POST["issuer_type"].strip()!="" else None if "issuer_type" in col_names else None
            obj.collateral_eligibity = request.POST["collateral_eligibity"] if request.POST["collateral_eligibity"].strip()!="" else None if "collateral_eligibity" in col_names else None
            obj.rating_available = request.POST["rating_available"] if request.POST["rating_available"].strip()!="" else None if "rating_available" in col_names else None
            obj.collateral_rating = request.POST["collateral_rating"] if request.POST["collateral_rating"].strip()!="" else None if "collateral_rating" in col_names else None
            obj.residual_maturity = request.POST["residual_maturity"] if request.POST["residual_maturity"].strip()!="" else None if "residual_maturity" in col_names else None
            obj.basel_collateral_type = request.POST["basel_collateral_type"] if request.POST["basel_collateral_type"].strip()!="" else None if "basel_collateral_type" in col_names else None
            obj.basel_collateral_subtype = request.POST["basel_collateral_subtype"] if request.POST["basel_collateral_subtype"].strip()!="" else None if "basel_collateral_subtype" in col_names else None
            obj.basel_collateral_code = request.POST["basel_collateral_code"] if request.POST["basel_collateral_code"].strip()!="" else None if "basel_collateral_code" in col_names else None
            obj.basel_collateral_rating = request.POST["basel_collateral_rating"] if request.POST["basel_collateral_rating"].strip()!="" else None if "basel_collateral_rating" in obj else None
            obj.soverign_issuer = request.POST["soverign_issuer"] if request.POST["soverign_issuer"].strip()!="" else None if "soverign_issuer" in col_names else None
            obj.other_issuer = request.POST["other_issuer"] if request.POST["other_issuer"].strip()!="" else None if "other_issuer" in col_names else None


        #
        #
        if tab_status == "pd":
            obj.date = request.POST["date"] if request.POST["date"].strip()!="" else None
            obj.factor_1 = request.POST["factor_1"] if request.POST["factor_1"].strip()!="" else None
            obj.factor_2 = request.POST["factor_2"] if request.POST["factor_2"].strip()!="" else None
            obj.factor_3 = request.POST["factor_3"] if request.POST["factor_3"].strip()!="" else None
            obj.factor_4 = request.POST["factor_4"] if request.POST["factor_4"].strip()!="" else None
            obj.factor_5 = request.POST["factor_5"] if request.POST["factor_5"].strip()!="" else None
            obj.factor_6 = request.POST["factor_6"] if request.POST["factor_6"].strip()!="" else None
            obj.default_col = request.POST["default_col"] if request.POST["default_col"].strip()!="" else None
            obj.mgmt_overlay_1 = request.POST["mgmt_overlay_1"] if request.POST["mgmt_overlay_1"].strip()!="" else None
            obj.mgmt_overlay_2 = request.POST["mgmt_overlay_2"] if request.POST["mgmt_overlay_2"].strip()!="" else None

        #
        #
        if tab_status == "lgd":
            obj.date = request.POST["date"] if request.POST["date"].strip()!="" else None
            obj.ead_os = request.POST["ead_os"] if request.POST["ead_os"].strip()!="" else None
            obj.pv_cashflows = request.POST["pv_cashflows"] if request.POST["pv_cashflows"].strip()!="" else None
            obj.pv_cost = request.POST["pv_cost"] if request.POST["pv_cost"].strip()!="" else None
            obj.beta_value = request.POST["beta_value"] if request.POST["beta_value"].strip()!="" else None
            obj.sec_flag = request.POST["sec_flag"] if request.POST["sec_flag"].strip()!="" else None
            obj.factor_4 = request.POST["factor_4"] if request.POST["factor_4"].strip()!="" else None
            obj.factor_5 = request.POST["factor_5"] if request.POST["factor_5"].strip()!="" else None
            obj.avg_1 = request.POST["factor_5"] if request.POST["factor_5"].strip()!="" else None
            obj.avg_2 = request.POST["factor_5"] if request.POST["factor_5"].strip()!="" else None
            obj.avg_3 = request.POST["factor_5"] if request.POST["factor_5"].strip()!="" else None
            obj.avg_4 = request.POST["factor_5"] if request.POST["factor_5"].strip()!="" else None
            obj.avg_5 = request.POST["factor_5"] if request.POST["factor_5"].strip()!="" else None
            obj.mgmt_overlay_1 = request.POST["mgmt_overlay_1"] if request.POST["mgmt_overlay_1"].strip()!="" else None
            obj.mgmt_overlay_2 = request.POST["mgmt_overlay_2"] if request.POST["mgmt_overlay_2"].strip()!="" else None

        #
        #
        if tab_status == "stage":
            obj.date = request.POST["date"] if request.POST["date"].strip()!="" else None
            obj.old_rating = request.POST["old_rating"] if request.POST["old_rating"].strip()!="" else None
            obj.new_rating = request.POST["new_rating"] if request.POST["new_rating"].strip()!="" else None
            obj.rating_3 = request.POST["rating_3"] if request.POST["rating_3"].strip()!="" else None
            obj.rating_4 = request.POST["rating_4"] if request.POST["rating_4"].strip()!="" else None
            obj.rating_5 = request.POST["rating_5"] if request.POST["rating_5"].strip()!="" else None
            obj.rating_6 = request.POST["rating_6"] if request.POST["rating_6"].strip()!="" else None
            obj.rating_7 = request.POST["rating_7"] if request.POST["rating_7"].strip()!="" else None
            obj.day_bucket_1 = request.POST["day_bucket_1"] if request.POST["day_bucket_1"].strip()!="" else None
            obj.day_bucket_2 = request.POST["day_bucket_2"] if request.POST["day_bucket_2"].strip()!="" else None
            obj.day_bucket_3 = request.POST["day_bucket_3"] if request.POST["day_bucket_3"].strip()!="" else None
            obj.day_bucket_4 = request.POST["day_bucket_4"] if request.POST["day_bucket_4"].strip()!="" else None
            obj.day_bucket_5 = request.POST["day_bucket_5"] if request.POST["day_bucket_5"].strip()!="" else None
            obj.day_bucket_6 = request.POST["day_bucket_6"] if request.POST["day_bucket_6"].strip()!="" else None
            obj.day_bucket_7 = request.POST["day_bucket_7"] if request.POST["day_bucket_7"].strip()!="" else None
            obj.day_bucket_8 = request.POST["day_bucket_8"] if request.POST["day_bucket_8"].strip()!="" else None
            obj.day_bucket_9 = request.POST["day_bucket_9"] if request.POST["day_bucket_9"].strip()!="" else None
            obj.day_bucket_10 = request.POST["day_bucket_10"] if request.POST["day_bucket_10"].strip()!="" else None
            obj.day_bucket_11 = request.POST["day_bucket_11"] if request.POST["day_bucket_11"].strip()!="" else None
            obj.day_bucket_12 = request.POST["day_bucket_12"] if request.POST["day_bucket_12"].strip()!="" else None
            obj.day_bucket_13 = request.POST["day_bucket_13"] if request.POST["day_bucket_13"].strip()!="" else None
            obj.day_bucket_14 = request.POST["day_bucket_14"] if request.POST["day_bucket_14"].strip()!="" else None
            obj.day_bucket_15 = request.POST["day_bucket_15"] if request.POST["day_bucket_15"].strip()!="" else None
            obj.criteria = request.POST["criteria"] if request.POST["criteria"].strip()!="" else None
            obj.cooling_period_1 = request.POST["cooling_period_1"] if request.POST["cooling_period_1"].strip()!="" else None
            obj.cooling_period_2 = request.POST["cooling_period_2"] if request.POST["cooling_period_2"].strip()!="" else None
            obj.cooling_period_3 = request.POST["cooling_period_3"] if request.POST["cooling_period_3"].strip()!="" else None
            obj.cooling_period_4 = request.POST["cooling_period_4"] if request.POST["cooling_period_4"].strip()!="" else None
            obj.cooling_period_5 = request.POST["cooling_period_5"] if request.POST["cooling_period_5"].strip()!="" else None
            obj.rbi_window = request.POST["rbi_window"] if request.POST["rbi_window"].strip()!="" else None
            obj.mgmt_overlay_1 = request.POST["mgmt_overlay_1"] if request.POST["mgmt_overlay_1"].strip()!="" else None
            obj.mgmt_overlay_2 = request.POST["mgmt_overlay_2"] if request.POST["mgmt_overlay_2"].strip()!="" else None

        #
        #
        if tab_status == "ead":
            obj.date = request.POST["date"] if request.POST["date"].strip()!="" else None
            obj.outstanding_amount = request.POST["outstanding_amount"] if request.POST["outstanding_amount"].strip()!="" else None
            obj.undrawn_upto_1_yr = request.POST["undrawn_upto_1_yr"] if request.POST["undrawn_upto_1_yr"].strip()!="" else None
            obj.undrawn_greater_than_1_yr = request.POST["undrawn_greater_than_1_yr"] if request.POST["undrawn_greater_than_1_yr"].strip()!="" else None
            obj.collateral_1_value = request.POST["collateral_1_value"] if request.POST["collateral_1_value"].strip()!="" else None
            obj.collateral_1_rating = request.POST["collateral_1_rating"] if request.POST["collateral_1_rating"].strip()!="" else None
            obj.collateral_1_residual_maturity = request.POST["collateral_1_residual_maturity"] if request.POST["collateral_1_residual_maturity"].strip()!="" else None
            obj.collateral_2_value = request.POST["collateral_2_value"] if request.POST["collateral_2_value"].strip()!="" else None
            obj.collateral_2_rating = request.POST["collateral_2_rating"] if request.POST["collateral_2_rating"].strip()!="" else None
            obj.collateral_2_residual_maturity = request.POST["collateral_2_residual_maturity"] if request.POST["collateral_2_residual_maturity"].strip()!="" else None

        #
        #
        obj.edited_by = request.user
        obj.edited_on = timezone.now()

        #
        # Audit Trail
        helpers.audit_trail(request, {
            "parent" : tab_status,
            "edited_data" : True,
            "params":{"handler_table": "initial", "selected_ids":[obj.id]}
        })

        obj.save()

        messages.success(request, "Record Edited Successfully")
        return redirect("manage_imports", tab_status)

    else:
        messages.error(request, "Operation Failed")
    return redirect("manage_imports", tab_status)


#**********************************************************************
# METHOD TO MOVE DATA OF RELEVANT FINAL MODELS - SELECTED
#**********************************************************************
def move_all_to_final(request, tab_status=None):
    if tab_status is not None:

        ids = request.POST.getlist("checkbox_one",None)
        not_found = False
        no_account = False
        record_failed = True

        if len(ids) == 0:
            messages.error(request, "Operation Failed. No records selected")
            return redirect("manage_imports", tab_status)

        for id in ids:
            try:
                obj = constants.TAB_ACTIVE[tab_status][3].get(pk = id)

                if obj.account_no is None:
                    no_account = True
                else:
                    if background_tasks.move_record(request, tab_status, obj):
                        record_failed = False

            except ObjectDoesNotExist:
                not_found = True

        #
        #
        if not_found:
            messages.error(request, "Operation Failed. One/Multiple records not Found. Failed to Move data.")
            return redirect("manage_imports", tab_status)
        elif no_account and record_failed:
            messages.error(request, "Some Records Cannot Be Moved. Account Number is not found in master. Please update the records")
            return redirect("manage_imports", tab_status)
        else:
            messages.success(request, "Records Moved Successfully")
            return redirect("manage_imports", tab_status)
    else:
        messages.success(request, "Records Moved Successfully")
    return redirect("manage_imports")


#**********************************************************************
# METHOD TO EDIT DATA OF RELEVANT MODELS - SINGLE
#**********************************************************************
def move_to_final(request, tab_status=None, ins=None):
    if ins is not None:
        try:
            obj = constants.TAB_ACTIVE[tab_status][3].get(pk = ins)
        except ObjectDoesNotExist:
            messages.error(request, "Operation Failed")
            return redirect("manage_imports", tab_status)

        if obj.account_no is None:
            messages.error(request, "Record Cannot Be Moved. Account Number is not found in master. Please update the record")
            return redirect("manage_imports", tab_status)

        if background_tasks.move_record(request, tab_status, obj):

            messages.success(request, "Record Moved Successfully")
        else:
            messages.error(request, "Operation Failed.")
    else:
        messages.error(request, "Operation Failed.")
    return redirect("manage_imports", tab_status)




#**********************************************************************
# ENDPOINT: MAIN DATA - ALL IN BACKGROUND
#**********************************************************************
def move_data_bg_process(request, tab_status=None):
    if tab_status is not None and tab_status in constants.TAB_ACTIVE.keys():

        json_res = background_tasks.move_data_bg_process(request, tab_status)
        return JsonResponse(json_res)
    return JsonResponse({"ret":False})


#**********************************************************************
# ENDPOINT: MAIN DATA
#**********************************************************************
def show_final_records(request, tab_status=None):
    data = defaultdict()

    if tab_status is None:
        tab_status = "pd"

    data["tab_status"] = tab_status
    data["tab_active"] = constants.TAB_ACTIVE[tab_status][0]
    data["content_template"] = constants.TAB_ACTIVE[tab_status][1]
    data["js_files"] = ['custom_js/imports.js']
    data["sidebar_active"] = 4

    #
    # TAB- PD
    #==============================================================
    if tab_status == "pd":
        product_qry = """select product_name from app_basel_product_master where id = (select distinct(product_id) from app_collateral where account_no_id = app_pd_final.account_no_id)"""

        results = constants.TAB_ACTIVE[tab_status][4].extra(select={'product_name': product_qry}).select_related("account_no")

        results = results.values('id', 'date', 'account_no_id', 'product_name', 'factor_1', 'factor_2', 'factor_3', 'factor_4', 'default_col', 'factor_5', 'factor_6', 'mgmt_overlay_1', 'mgmt_overlay_2', Account_No = F('account_no__account_no'), cin = F('account_no__cin'), sectors = F('account_no__sectors'), account_type = F('account_no__account_type'))

    #
    # TAB- LGD
    #==============================================================
    if tab_status == "lgd":

        product_qry = """select product_name from app_basel_product_master where id = (select distinct(product_id) from app_collateral where account_no_id = app_lgd_final.account_no_id)"""

        results = constants.TAB_ACTIVE[tab_status][4].extra(select={'product_name': product_qry}).select_related("account_no")

        results = results.values('id', 'date', 'account_no_id', 'ead_os', 'pv_cashflows', 'pv_cost', 'beta_value', 'sec_flag', 'factor_4', 'factor_5', 'avg_1', 'avg_2', 'avg_3', 'avg_4', 'avg_5', 'mgmt_overlay_1', 'mgmt_overlay_2', Account_No = F('account_no__account_no'), cin = F('account_no__cin'), sectors = F('account_no__sectors'), account_type = F('account_no__account_type')).order_by("id")

    #
    # TAB- Stage
    #==============================================================
    if tab_status == "stage":

        product_qry = """select product_name from app_basel_product_master where id = (select distinct(product_id) from app_collateral where account_no_id = app_stage_final.account_no_id)"""

        results = constants.TAB_ACTIVE[tab_status][4].extra(select={'product_name': product_qry}).select_related("account_no")

        results = results.values('id', 'date', 'account_no_id', 'product_name', 'old_rating', 'new_rating', 'rating_3', 'rating_4', 'rating_5', 'rating_6', 'rating_7', 'day_bucket_1', 'day_bucket_2', 'day_bucket_3', 'day_bucket_4', 'day_bucket_5', 'day_bucket_6', 'day_bucket_7', 'day_bucket_8', 'day_bucket_9', 'day_bucket_10', 'day_bucket_11', 'day_bucket_12','day_bucket_13', 'day_bucket_14', 'day_bucket_15', 'criteria', 'cooling_period_1', 'cooling_period_2', 'cooling_period_3', 'cooling_period_4', 'cooling_period_5', 'rbi_window', 'mgmt_overlay_1', 'mgmt_overlay_2', Account_No = F('account_no__account_no'), cin = F('account_no__cin'), sectors = F('account_no__sectors'), account_type = F('account_no__account_type')).order_by("id")


    #
    # TAB- EAD
    #==============================================================
    if tab_status == "ead":

        data["counter"] = [1]
        counters = constants.TAB_ACTIVE[tab_status][4].raw("""select max(ads.id) as id from (select count(*) as id from app_collateral group by account_no_id) ads""")

        for x in counters:
            data["counter"] = range(1, int(x.id)+1)

        qry = """
            select ED.date, ED.id, ED.outstanding_amount, ED.undrawn_upto_1_yr, ED.undrawn_greater_than_1_yr, AC.account_no as Account_no, AC.account_type, AC.sectors, AC.cin, C.collateral_value, C.collateral_rating as c_rating, C.collateral_residual_maturity as c_r_maturity, BP.product_name, BP.product_code, BC.collateral_code, BC.collateral_type, BC.issuer_type, BC.collateral_eligibity, BC.rating_available, BC.collateral_rating as b_c_rating, BC.residual_maturity, BC.basel_collateral_type, BC.basel_collateral_subtype, BC.basel_collateral_code, BC.basel_collateral_rating, BC.soverign_issuer, BC.other_issuer
            from app_ead_final ED
            left join app_accountmaster AC on AC.id = ED.account_no_id
            left join app_collateral C on C.account_no_id = AC.id
            left join app_basel_product_master BP on BP.id = C.product_id
            left join app_basel_collateral_master BC on BC.id = C.collateral_code_id
        """

        items_list = {}

        results = constants.TAB_ACTIVE[tab_status][4].raw(qry)

        for row in results:
            items_list[row.id] = {
                "date":row.date,
                "Account_no":row.Account_no,
                "account_type":row.account_type,
                "cin":row.cin,
                "sectors":row.sectors,
                "outstanding_amount":row.outstanding_amount,
                "undrawn_upto_1_yr":row.undrawn_upto_1_yr,
                "undrawn_greater_than_1_yr":row.undrawn_greater_than_1_yr,
                "account_no":row.account_no,
                "product_name":row.product_name,
                "product_code":row.product_code,
                "collaterals":[]
            }

        for row in results:
            items_list[row.id]["collaterals"].append({
                "collateral_value":row.collateral_value,
                "c_rating":row.c_rating,
                "c_r_maturity":row.c_r_maturity,
                "collateral_code":row.collateral_code,
                "collateral_type":row.collateral_type,
                "issuer_type":row.issuer_type,
                "collateral_eligibity":row.collateral_eligibity,
                "rating_available":row.rating_available,
                "b_c_rating":row.b_c_rating,
                "residual_maturity":row.residual_maturity,
                "basel_collateral_type":row.basel_collateral_type,
                "basel_collateral_subtype":row.basel_collateral_subtype,
                "basel_collateral_code":row.basel_collateral_code,
                "basel_collateral_rating":row.basel_collateral_rating,
                "soverign_issuer":row.soverign_issuer,
                "other_issuer":row.other_issuer,
                "bg_color":helpers.bg_color_codes(),
            })



    #
    # PAGINATIONS
    #==============================================================

    if tab_status != "ead":
        results = results.order_by("id")

        page = request.GET.get('page', 1)

        paginator = Paginator(results, 100)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

    else:
        results = items_list

    data["tab_status"] = tab_status
    data["tab_active"] = constants.TAB_ACTIVE[tab_status][0]
    data["content_template"] = constants.TAB_ACTIVE[tab_status][7]
    data["js_files"] = ['custom_js/imports.js']
    data["sidebar_active"] = 4
    data["items_list"] = results

    return render(request, "administrator/index.html", data)



#**********************************************************************
# ENDPOINT: GET MISSING ACCOUNTS
#**********************************************************************

class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def download_missing_accounts_csv(request):
    """A view that streams a large CSV file."""
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.

    result = []
    result.append({"Account No.":"Acoount No."})
    rows = list(AccountMissing.objects.all().values_list('account_no'))

    for row in rows:
        result.append(row)

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    return StreamingHttpResponse(
        (writer.writerow(row) for row in result),
        content_type="text/csv"
    )


#**********************************************************************
# ENDPOINT: GENERATE REPORT - PD
#**********************************************************************

def pd_report(request, s_type=0):

    ret = False
    start_date = request.POST.get("start_date", None)
    end_date = request.POST.get("end_date", None)
    account_no = request.POST.get("account_no", None)
    id_selected = request.POST.getlist("checkbox_one", None)

    #
    #
    try:
        if start_date is not None:
            if start_date.strip() == "":
                start_date = None
    except AttributeError:
        pass

    try:
        if end_date is not None:
            if end_date.strip() == "":
                end_date = None
    except AttributeError:
        pass

    try:
        if account_no is not None:
            if account_no.strip() == "":
                account_no = None
            else:
                account_no = [helpers.clean_data(x) for x in account_no.split(",")]
    except AttributeError:
        pass
    #
    #

    if account_no is not None or start_date is not None or end_date is not None:
        id_selected = None


    #
    #

    ret = background_tasks.pd_report(request, start_date = start_date, end_date = end_date, account_no = account_no, s_type = s_type, id_selected = id_selected)
    if ret:

        results = PD_Report.objects

        if id_selected is not None:
            if len(id_selected) > 0:
                results = results.filter(id__in = id_selected)
        else:
            if start_date is None and end_date is None and account_no is None:
                results = results.all()

            if start_date is not None:
                if end_date is not None:
                    results = results.filter(date__gte = start_date, date__lte = end_date)
                else:
                    results = results.filter(date__gte = start_date)

            if account_no is not None:
                results = results.filter(account_no__account_no__in = account_no)


        product_qry = """select product_name from app_basel_product_master where id = (select distinct(product_id) from app_collateral where account_no_id = app_pd_report.account_no_id)"""

        results = results.extra(select={'product_name': product_qry}).select_related('account_no').values('id', 'date' ,'product_name', 'factor_1', 'factor_2', 'factor_3', 'factor_4', 'factor_5', 'factor_6', 'default_col', 'mgmt_overlay_1', 'mgmt_overlay_2', 'intercept', 'coeff_fact1', 'coeff_fact2', 'coeff_fact3', 'coeff_fact4', 'zscore', 'pd', Account_no = F('account_no__account_no'), cin = F('account_no__cin'), account_type = F('account_no__account_type'), sectors = F('account_no__sectors'))


    if request.is_ajax():
        if ret:
            return JsonResponse({"ret":ret, "msg":"PD Report Created Successfully", "results":list(results)})
        else:
            return JsonResponse({"ret":ret, "msg":"PD Report Creation Failed"})
    else:
        messages.success(request, "Report Generated Successfully")

        if account_no is None and start_date is not None and end_date is not None and id_selected is not None:
            rev = reverse("show_reports")
            params = request.POST.urlencode()
            rev = '{}?{}'.format(rev, params)
            return redirect(rev)
        else:
            return redirect("show_reports", "pd")

#**********************************************************************
# ENDPOINT: GENERATE REPORT - LGD
#**********************************************************************
def lgd_report(request, s_type=0):
    ret = False
    start_date = request.POST.get("start_date", None)
    end_date = request.POST.get("end_date", None)
    account_no = request.POST.get("account_no", None)
    id_selected = request.POST.getlist("checkbox_one", None)

    #
    #
    try:
        if start_date.strip() == "":
            start_date = None
    except AttributeError:
        pass

    try:
        if end_date.strip() == "":
            end_date = None
    except AttributeError:
        pass

    try:
        if account_no.strip() == "":
            account_no = None
    except AttributeError:
        pass

    #
    #
    ret = background_tasks.lgd_report(request, start_date = start_date, end_date = end_date, account_no = account_no, s_type = s_type, id_selected = id_selected)
    if ret:

        results = LGD_Report.objects

        if len(id_selected) > 0:
            results = results.filter(id__in = id_selected)
        else:

            if start_date is None and end_date is None and account_no is None:
                results = results.all()

            if start_date is not None:
                if end_date is not None:
                    results = results.filter(date__gte = start_date, date__lte = end_date)
                else:
                    results = results.filter(date__gte = start_date)

            if account_no is not None:
                results = results.filter(account_no__account_no__in = account_no)

        product_qry = """select product_name from app_basel_product_master where id = (select distinct(product_id) from app_collateral where account_no_id = app_pd_report.account_no_id)"""

        results = results.extra(select={'product_name': product_qry}).select_related('account_no').values('id','date', 'product_name', 'ead_os', 'pv_cost', 'pv_cashflows', 'beta_value', 'sec_flag', 'factor_4', 'factor_5', 'avg_1', 'avg_2', 'avg_3', 'avg_4', 'avg_5', 'mgmt_overlay_1', 'mgmt_overlay_2', 'rec_rate', 'est_rr', 'est_lgd', 'final_lgd',  Account_no = F('account_no__account_no'), cin = F('account_no__cin'), account_type = F('account_no__account_type'), sectors = F('account_no__sectors'))

    if request.is_ajax():
        if ret:
            return JsonResponse({"ret":ret, "msg":"LGD Report Created Successfully", "results":list(results)})
        else:
            return JsonResponse({"ret":ret, "msg":"LGD Report Creation Failed"})
    else:
        messages.success(request, "Report Generated Successfully")

        if account_no is None and start_date is not None and end_date is not None and id_selected is not None:
            rev = reverse("show_reports")
            params = request.POST.urlencode()
            rev = '{}?{}'.format(rev, params)
            return redirect(rev)
        else:
            return redirect("show_reports", "lgd")


#**********************************************************************
# ENDPOINT: GENERATE REPORT - STAGE
#**********************************************************************
def stage_report(request, s_type=0):

    ret = False
    start_date = request.POST.get("start_date", None)
    end_date = request.POST.get("end_date", None)
    account_no = request.POST.get("account_no", None)
    id_selected = request.POST.getlist("checkbox_one", None)

    try:
        if start_date.strip() == "":
            start_date = None
    except AttributeError:
        pass

    try:
        if end_date.strip() == "":
            end_date = None
    except AttributeError:
        pass

    try:
        if account_no.strip() == "":
            account_no = None
    except AttributeError:
        pass

    #
    #
    ret = background_tasks.stage_report(request, start_date = start_date, end_date = end_date, account_no = account_no, s_type = s_type, id_selected = id_selected)
    if ret:

        results = Stage_Report.objects

        if len(id_selected) > 0:
            results = results.filter(id__in = id_selected)
        else:

            if start_date is None and end_date is None and account_no is None:
                results = results.all()

            if start_date is not None:
                if end_date is not None:
                    results = results.filter(date__gte = start_date, date__lte = end_date)
                else:
                    results = results.filter(date__gte = start_date)

            if account_no is not None:
                results = results.filter(account_no__account_no__in = account_no)

        product_qry = """select product_name from app_basel_product_master where id = (select distinct(product_id) from app_collateral where account_no_id = app_stage_report.account_no_id)"""

        results = results.extra(select={'product_name': product_qry}).values('id', 'date', 'stage', 'state', 'old_rating', 'new_rating', 'rating_3', 'rating_4', 'rating_5', 'rating_6', 'rating_7', 'day_bucket_1', 'day_bucket_2', 'day_bucket_3', 'day_bucket_4', 'day_bucket_5', 'day_bucket_6', 'day_bucket_7', 'day_bucket_8', 'day_bucket_9', 'day_bucket_10', 'day_bucket_11', 'day_bucket_12', 'day_bucket_13', 'day_bucket_14', 'day_bucket_15', 'criteria', 'cooling_period_1', 'cooling_period_2', 'cooling_period_3', 'cooling_period_4', 'cooling_period_5', 'rbi_window', 'mgmt_overlay_1', 'mgmt_overlay_2', Account_no = F('account_no__account_no'), cin = F('account_no__cin'), account_type = F('account_no__account_type'), sectors = F('account_no__sectors'))

    if request.is_ajax():
        if ret:
            return JsonResponse({"ret":ret, "msg":"Stage Report Created Successfully", "results":list(results)})
        else:
            return JsonResponse({"ret":ret, "msg":"Stage Report Creation Failed"})
    else:
        messages.success(request, "Report Generated Successfully")

        if account_no is None and start_date is not None and end_date is not None and id_selected is not None:
            rev = reverse("show_reports")
            params = request.POST.urlencode()
            rev = '{}?{}'.format(rev, params)
            return redirect(rev)
        else:
            return redirect("show_reports", "stage")



#**********************************************************************
# ENDPOINT: GENERATE REPORT - STAGE
#**********************************************************************
def ead_report(request):

    ret = False
    start_date = request.POST.get("start_date", None)
    end_date = request.POST.get("end_date", None)
    account_no = request.POST.get("account_no", None)
    id_selected = request.POST.getlist("checkbox_one", None)

    #
    #
    try:
        if start_date.strip() == "":
            start_date = None
    except AttributeError:
        pass

    try:
        if end_date.strip() == "":
            end_date = None
    except AttributeError:
        pass

    try:
        if account_no.strip() == "":
            account_no = None
    except AttributeError:
        pass


    #
    #
    ret = background_tasks.ead_report(request, start_date = start_date, end_date = end_date, account_no = account_no)
    if ret:

        qry = """
            select ED.date, ED.id, ED.outstanding_amount, ED.undrawn_upto_1_yr, ED.undrawn_greater_than_1_yr, AC.account_no as Account_no, AC.account_type, AC.sectors, AC.cin, C.collateral_value, C.collateral_rating as c_rating, C.collateral_residual_maturity as c_r_maturity, BP.product_name, BP.product_code, BC.collateral_code, BC.collateral_type, BC.issuer_type, BC.collateral_eligibity, BC.rating_available, BC.collateral_rating as b_c_rating, BC.residual_maturity, BC.basel_collateral_type, BC.basel_collateral_subtype, BC.basel_collateral_code, BC.basel_collateral_rating, BC.soverign_issuer, BC.other_issuer, ED.ead_total
            from app_ead_report ED
            left join app_accountmaster AC on AC.id = ED.account_no_id
            left join app_collateral C on C.account_no_id = AC.id
            left join app_basel_product_master BP on BP.id = C.product_id
            left join app_basel_collateral_master BC on BC.id = C.collateral_code_id order by ED.id
        """

        items_list = {}

        results = constants.TAB_ACTIVE["ead"][4].raw(qry)

        for row in results:
            items_list[row.id] = {
                "date":row.date,
                "Account_no":row.Account_no,
                "account_type":row.account_type,
                "cin":row.cin,
                "sectors":row.sectors,
                "outstanding_amount":row.outstanding_amount,
                "undrawn_upto_1_yr":row.undrawn_upto_1_yr,
                "undrawn_greater_than_1_yr":row.undrawn_greater_than_1_yr,
                "product_name":row.product_name,
                "product_code":row.product_code,
                "collaterals":[],
                "ead_total":row.ead_total,
            }

        for row in results:
            items_list[row.id]["collaterals"].append({
                "collateral_value":row.collateral_value,
                "c_rating":row.c_rating,
                "c_r_maturity":row.c_r_maturity,
                "collateral_code":row.collateral_code,
                "collateral_type":row.collateral_type,
                "issuer_type":row.issuer_type,
                "collateral_eligibity":row.collateral_eligibity,
                "rating_available":row.rating_available,
                "b_c_rating":row.b_c_rating,
                "residual_maturity":row.residual_maturity,
                "basel_collateral_type":row.basel_collateral_type,
                "basel_collateral_subtype":row.basel_collateral_subtype,
                "basel_collateral_code":row.basel_collateral_code,
                "basel_collateral_rating":row.basel_collateral_rating,
                "soverign_issuer":row.soverign_issuer,
                "other_issuer":row.other_issuer,
                "bg_color":helpers.bg_color_codes(),
            })


    if request.is_ajax():
        if ret:
            return JsonResponse({"ret":ret, "msg":"EAD Report Created Successfully", "results":list(items_list)})
        else:
            return JsonResponse({"ret":ret, "msg":"EAD Report Creation Failed"})
    else:
        messages.success(request, "Report Generated Successfully")

        if account_no is None and start_date is not None and end_date is not None and id_selected is not None:
            rev = reverse("show_reports")
            params = request.POST.urlencode()
            rev = '{}?{}'.format(rev, params)
            return redirect(rev)
        else:
            return redirect("show_reports", "ead")



#**********************************************************************
# ENDPOINT: REPORT - SHOW
#**********************************************************************
def show_reports(request, tab_status=None):

    data = defaultdict()

    account_no = None
    start_date = None
    end_date = None

    if tab_status is None:
        tab_status = "pd"

    #
    # GET REQUESTS
    #==============================================================

    if request.GET:
        start_date = request.GET.get("start_date").strip() if request.GET.get("start_date") else None
        end_date = request.GET.get("end_date").strip() if request.GET.get("end_date") else None
        acc_list = [helpers.clean_data(x) for x in request.GET.get("account_no").strip().split(",")]
        account_no = list(filter(None, acc_list))

    if request.POST:
        start_date = request.POST.get("start_date").strip() if request.POST.get("start_date") else None
        end_date = request.POST.get("end_date").strip() if request.POST.get("end_date") else None
        acc_list = [helpers.clean_data(x) for x in request.POST.get("account_no").strip().split(",")]
        account_no = list(filter(None, acc_list))
        messages.success(request, "Search Results Generated Successfully")

    if account_no is not None:
        if len(account_no) == 0:
            account_no = None

    #
    # TAB- PD
    #==============================================================
    if tab_status == "pd":
        results = PD_Report.objects

        product_qry = """select product_name from app_basel_product_master where id = (select distinct(product_id) from app_collateral where account_no_id = app_pd_report.account_no_id)"""

        results = results.extra(select={'product_name': product_qry}).select_related('account_no')

        if start_date is None and end_date is None and account_no is None:
            results = results.all()

        if start_date is not None:
            if end_date is not None:
                results = results.filter(date__gte = start_date, date__lte = end_date)
            else:
                results = results.filter(date__gte = start_date)

        if account_no is not None:
            for i in account_no:
                acc = [x[0] for x in AccountMaster.objects.filter(account_no__icontains = i).values_list("id")]
                results = results.filter(Q(account_no_id__in = acc))

        results = results.values('id', 'date', 'account_no__account_no', 'product_name', 'factor_1', 'factor_2', 'factor_3', 'factor_4', 'factor_5', 'factor_6', 'default_col', 'mgmt_overlay_1', 'mgmt_overlay_2', 'intercept', 'coeff_fact1', 'coeff_fact2', 'coeff_fact3', 'coeff_fact4', 'zscore', 'pd', Account_No = F('account_no__account_no'), cin = F('account_no__cin'), sectors = F('account_no__sectors'), account_type = F('account_no__account_type')).order_by("id")


    #
    # TAB- LGD
    #==============================================================
    if tab_status == "lgd":
        results = LGD_Report.objects

        product_qry = """select product_name from app_basel_product_master where id = (select distinct(product_id) from app_collateral where account_no_id = app_lgd_report.account_no_id)"""

        results = results.extra(select={'product_name': product_qry}).select_related('account_no')

        if start_date is None and end_date is None and account_no is None:
            results = results.all()

        if start_date is not None:
            if end_date is not None:
                results = results.filter(date__gte = start_date, date__lte = end_date)
            else:
                results = results.filter(date__gte = start_date)

        if account_no is not None:
            for i in account_no:
                acc = [x[0] for x in AccountMaster.objects.filter(account_no__icontains = i).values_list("id")]
                results = results.filter(Q(account_no_id__in = acc))

        results = results.values('id', 'date', 'account_no__account_no', 'product_name', 'ead_os', 'pv_cashflows', 'pv_cost', 'beta_value', 'factor_5', 'sec_flag', 'factor_4', 'factor_5', 'avg_1', 'avg_2', 'avg_3', 'avg_4', 'avg_5', 'mgmt_overlay_1', 'mgmt_overlay_2', 'rec_rate', 'est_rr', 'est_lgd', 'final_lgd', Account_No = F('account_no__account_no'), cin = F('account_no__cin'), sectors = F('account_no__sectors'), account_type = F('account_no__account_type')).order_by("id")

    #
    # TAB- STAGE
    #==============================================================
    if tab_status == "stage":
        results = Stage_Report.objects

        product_qry = """select product_name from app_basel_product_master where id = (select distinct(product_id) from app_collateral where account_no_id = app_stage_report.account_no_id)"""

        results = results.extra(select={'product_name': product_qry}).select_related('account_no')

        if start_date is None and end_date is None and account_no is None:
            results = results.all()

        if start_date is not None:
            if end_date is not None:
                results = results.filter(date__gte = start_date, date__lte = end_date)
            else:
                results = results.filter(date__gte = start_date)

        if account_no is not None:
            for i in account_no:
                acc = [x[0] for x in AccountMaster.objects.filter(account_no__icontains = i).values_list("id")]
                results = results.filter(Q(account_no_id__in = acc))

        results = results.values('id', 'date', 'account_no__account_no', 'product_name', 'stage', 'state', 'old_rating', 'new_rating', 'rating_3', 'rating_4', 'rating_5', 'rating_6', 'rating_7', 'day_bucket_1', 'day_bucket_2', 'day_bucket_3', 'day_bucket_4', 'day_bucket_5', 'day_bucket_6', 'day_bucket_7', 'day_bucket_8', 'day_bucket_9', 'day_bucket_10', 'day_bucket_11', 'day_bucket_12', 'day_bucket_13', 'day_bucket_14', 'day_bucket_15', 'criteria', 'cooling_period_1', 'cooling_period_2', 'cooling_period_3', 'cooling_period_4', 'cooling_period_5', 'rbi_window', 'mgmt_overlay_1', 'mgmt_overlay_2', Account_No = F('account_no__account_no'), cin = F('account_no__cin'), sectors = F('account_no__sectors'), account_type = F('account_no__account_type')).order_by("id")

    #
    # TAB- EAD
    #==============================================================
    if tab_status == "ead":

        where_clause = False
        dates_cond = ""
        acc_cond = ""

        #
        #

        if start_date is None and end_date is None and account_no is None:
            dates_cond = ""
        else:
            if start_date is not None:
                if end_date is not None:
                    dates_cond = " where ED.date >='{}' and ED.date <='{}'".format(start_date, end_date)
                    where_clause = True
                else:
                    dates_cond = " where ED.date >='{}'".format(start_date)
                    where_clause = True

        if account_no is not None:
            if where_clause:
                acc_cond = " and ED.account_no_id = {}".format(account_no)
            else:
                acc_cond = " where ED.account_no_id = {}".format(account_no)

        #
        #
        data["counter"] = [1]
        counters = constants.TAB_ACTIVE[tab_status][4].raw("""select max(ads.id) as id from (select count(*) as id from app_collateral group by account_no_id) ads""")

        for x in counters:
            data["counter"] = range(1, int(x.id)+1)

        qry = """
            select ED.date, ED.id, ED.outstanding_amount, ED.undrawn_upto_1_yr, ED.undrawn_greater_than_1_yr, AC.account_no as Account_no, AC.account_type, AC.sectors, AC.cin, C.collateral_value, C.collateral_rating as c_rating, C.collateral_residual_maturity as c_r_maturity, BP.product_name, BP.product_code, BC.collateral_code, BC.collateral_type, BC.issuer_type, BC.collateral_eligibity, BC.rating_available, BC.collateral_rating as b_c_rating, BC.residual_maturity, BC.basel_collateral_type, BC.basel_collateral_subtype, BC.basel_collateral_code, BC.basel_collateral_rating, BC.soverign_issuer, BC.other_issuer, ED.ead_total
            from app_ead_report ED
            left join app_accountmaster AC on AC.id = ED.account_no_id
            left join app_collateral C on C.account_no_id = AC.id
            left join app_basel_product_master BP on BP.id = C.product_id
            left join app_basel_collateral_master BC on BC.id = C.collateral_code_id {} {} and ED.account_no_id is not null order by ED.id
        """.format(dates_cond, acc_cond)

        items_list = {}

        results = constants.TAB_ACTIVE[tab_status][4].raw(qry)

        for row in results:
            items_list[row.id] = {
                "date":row.date,
                "Account_no":row.Account_no,
                "account_type":row.account_type,
                "cin":row.cin,
                "sectors":row.sectors,
                "outstanding_amount":row.outstanding_amount,
                "undrawn_upto_1_yr":row.undrawn_upto_1_yr,
                "undrawn_greater_than_1_yr":row.undrawn_greater_than_1_yr,
                "product_name":row.product_name,
                "product_code":row.product_code,
                "collaterals":[],
                "ead_total":row.ead_total,
            }

        for row in results:
            items_list[row.id]["collaterals"].append({
                "collateral_value":row.collateral_value,
                "c_rating":row.c_rating,
                "c_r_maturity":row.c_r_maturity,
                "collateral_code":row.collateral_code,
                "collateral_type":row.collateral_type,
                "issuer_type":row.issuer_type,
                "collateral_eligibity":row.collateral_eligibity,
                "rating_available":row.rating_available,
                "b_c_rating":row.b_c_rating,
                "residual_maturity":row.residual_maturity,
                "basel_collateral_type":row.basel_collateral_type,
                "basel_collateral_subtype":row.basel_collateral_subtype,
                "basel_collateral_code":row.basel_collateral_code,
                "basel_collateral_rating":row.basel_collateral_rating,
                "soverign_issuer":row.soverign_issuer,
                "other_issuer":row.other_issuer,
                "bg_color":helpers.bg_color_codes(),
            })

    #
    # PAGINATIONS
    #==============================================================
    if tab_status != "ead":
        page = request.GET.get('page', 1)

        paginator = Paginator(results, 100)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
    else:
        results = items_list


    #
    # DATA
    #==============================================================
    data["tab_status"] = tab_status
    data["tab_active"] = constants.TAB_ACTIVE[tab_status][0]
    data["content_template"] = constants.TAB_ACTIVE[tab_status][8]
    data["js_files"] = ['custom_js/imports.js']
    data["sidebar_active"] = 7
    data["items_list"] = results

    return render(request, "administrator/index.html", data)


#**********************************************************************
# ENDPOINT: UPLOAD COLLATERAl
#**********************************************************************

def collateral_upload(request):
    csv_file = request.FILES['formFile']

    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
        return redirect("manage_imports", "master")

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    csv_data = csv.DictReader(io_string, delimiter=',', quotechar='"')

    # Get header names
    column_names = csv_data.fieldnames

    # Get collateral Header names
    collateral_cols = [x for x in column_names if x not in ("account_no", "product_code")]

    # Dictionary for mapping errors
    err_msg = {"account_nos":[], "product_code":[], "collateral_code":[]}

    # Delete null records
    Collateral.objects.filter(Q(account_no__isnull = True) | Q(product__isnull = True) | Q(collateral_code__isnull = True)).delete()

    # Iterate through CSV
    for row in csv_data:

        # Account Instance
        try:
            account_ins = AccountMaster.objects.get(account_no = row["account_no"].strip())
        except:
            account_ins = None
            err_msg["account_nos"].append(row["account_no"])

        # Product Instance
        try:
            product_ins = Basel_Product_Master.objects.get(product_code = row["product_code"].strip())
        except:
            product_ins = None
            err_msg["product_code"].append(row["product_code"])

        #
        # Delete Collateral Enteries for account Number found
        # Collateral.objects.filter(account_no = account_ins).delete()

        only_product = []

        #
        # INSERT COLLATERAL
        #===================================================================
        for x in collateral_cols:

            #
            #
            if row[x].strip() != "":
                #
                #

                collateral_values = row[x].strip().split("|")

                try:

                    collateral_ins = Basel_Collateral_Master.objects.get(basel_collateral_code = collateral_values[0])

                    if account_ins is not None and product_ins is not None:
                        obj = Collateral.objects.create(
                            account_no = account_ins,
                            product = product_ins,
                            collateral_code = collateral_ins
                        )

                        try:
                            obj.collateral_value = collateral_values[1] if collateral_values[1].strip() !="" else None
                        except IndexError:
                            pass

                        try:
                            obj.collateral_rating = collateral_values[2] if collateral_values[2].strip() !="" else None
                        except IndexError:
                            pass



                        obj.save()

                except ObjectDoesNotExist:
                    if row[x].strip() != "":
                        err_msg["collateral_code"].append(row[x])
            else:
                only_product.append(None)

        #
        #
        only_product = list(filter(None, only_product))

        if len(only_product) == 0:
            if account_ins is not None and product_ins is not None:
                try:
                    obj = Collateral.objects.update_or_create(
                        account_no = account_ins,
                        product = product_ins
                    )
                except:
                    pass

    # Mapping Errors into message framework
    #=================================================================

    html = ["<p><strong>Errors found during Collateral Mapping Uploads </strong></p><hr/>"]
    if len(err_msg["account_nos"]) > 0:
        html.append('<p><strong>Account Nos not found</strong> : '+ ', '.join(set(err_msg["account_nos"]))+'</p>')

    if len(err_msg["product_code"]) > 0:
        html.append('<p><strong>Product Codes not found</strong> : '+ ', '.join(set(err_msg["product_code"]))+'</p>')

    if len(err_msg["collateral_code"]) > 0:
        html.append('<p><strong>Collateral Codes not found</strong> : '+ ', '.join(set(err_msg["collateral_code"]))+'</p>')

    if len(err_msg["account_nos"]) > 0 or len(err_msg["product_code"]) > 0 or len(err_msg["collateral_code"]) > 0:
        messages.error(request, ''.join(html))
    else:
        messages.success(request, "Collateral Data inserted without any error")

    return redirect("manage_imports", "master")



#**********************************************************************
# ENDPOINT: GET COLLATERAl DATA
#**********************************************************************

def get_collateral_data(request, ins=None):
    results = Collateral.objects.filter(account_no_id = int(ins)).select_related("acoount_no", "product", "collateral_code").values('id', 'product__product_name', 'product__product_code', 'product__product_catgory', 'product__basel_product', 'product__basel_product_code', 'product__drawn_cff', 'product__cff_upto_1_yr', 'product__cff_gt_1_yr', 'collateral_code__collateral_code', 'collateral_code__collateral_type', 'collateral_code__issuer_type', 'collateral_code__collateral_eligibity', 'collateral_code__rating_available', 'collateral_code__collateral_rating', 'collateral_code__residual_maturity', 'collateral_code__basel_collateral_type', 'collateral_code__basel_collateral_subtype', 'collateral_code__basel_collateral_code', 'collateral_code__basel_collateral_rating', 'collateral_code__soverign_issuer', 'collateral_code__other_issuer')

    return JsonResponse({"results":list(results)})


#**********************************************************************
# ENDPOINT: GET COLLATERAl DATA
#**********************************************************************

def delete_single_collateral_data(request):
    try:
        collaterals = Collateral.objects.get(pk = int(request.GET["id"]))

        #
        # Audit Trail
        helpers.audit_trail(request, {
            "parent" : "collateral map",
            "deleted_data" : True,
            "params":{"handler_table": "initial", "selected_ids":[collaterals.account_no_id], "all":False}
        })

        collaterals.delete()

    except:
        return HttpResponse(0)
    return HttpResponse(1)


#**********************************************************************
# ENDPOINT: DELETE COLLATERAl DATA - FOR AN ACCOUNT
#**********************************************************************

def delete_all_collaterals(request):
    collaterals = Collateral.objects.filter(account_no_id = int(request.GET["ids"]))
    #
    # Audit Trail
    helpers.audit_trail(request, {
        "parent" : "collateral map",
        "deleted_data" : True,
        "params":{"handler_table": "initial", "selected_ids":[int(request.GET["ids"])], "all":True}
    })

    collaterals.delete()

    return HttpResponse(1)


#**********************************************************************
# ENDPOINT: DELETE COLLATERALS
#**********************************************************************
def delete_collateral(request):
    Collateral.objects.all().delete()

    #
    # Audit Trail
    helpers.audit_trail(request, {
        "parent" : "collateral map",
        "deleted_data" : True,
        "params":{"handler_table": "initial", "selected_ids":[], "all":True}
    })

    messages.success(request, "Records Deleted Successfully")
    return HttpResponse(1)



#**********************************************************************
# ENDPOINT: DELETE FROM FINAL TABLE
#**********************************************************************

def delete_final_records(request, tab_status):
    ins_list = request.POST.getlist("checkbox_one", None)

    if len(ins_list) == 0:
        constants.TAB_ACTIVE[tab_status][4].all().delete()
    else:
        constants.TAB_ACTIVE[tab_status][4].filter(pk__in = ins_list).delete()
    messages.success(request, "Records Deleted Successfully")

    return HttpResponse("1")


#**********************************************************************
# ENDPOINT: DELETE FROM REPORTS TABLE
#**********************************************************************

def delete_report_records(request, tab_status):
    ins_list = request.POST.getlist("checkbox_one", None)

    if len(ins_list) == 0:
        constants.TAB_ACTIVE[tab_status][9].all().delete()
    else:
        constants.TAB_ACTIVE[tab_status][9].filter(pk__in = ins_list).delete()
    messages.success(request, "Records Deleted Successfully")

    return HttpResponse("1")


#**********************************************************************
# ENDPOINT: DOWNLOAD REPORTS
#**********************************************************************

def download_reports(request, tab_status=None, ftype=0):

    if request.POST["start_date"].strip() == "":
        start_date = None
    else:
        start_date = request.POST["start_date"].strip()

    if request.POST["end_date"].strip() == "":
        end_date = None
    else:
        end_date = request.POST["end_date"].strip()


    if ftype == 0:
        path = background_tasks.download_reports(tab_status=tab_status, start_date=start_date, end_date=end_date, ftype=0)
        if os.path.exists(path):
            with open(path, "rb") as report:
                data = report.read()
                response = HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename={}_Report.xlsx'.format(tab_status)
                return response
    elif ftype == 1:
        df = background_tasks.download_reports(tab_status=tab_status, start_date=start_date, end_date=end_date, ftype=1)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}_Report.csv'.format(tab_status)
        df.to_csv(path_or_buf=response, float_format='%.5f', index=False)
        return response
    else:
        return redirect("show_reports")


#**********************************************************************
# ENDPOINT: SHOW COLLATERALS
#**********************************************************************
def show_collateral_mapping(request):

    data = defaultdict()

    results = Collateral.objects.all().select_related('account_no', 'collateral_code', 'product').values('collateral_value', 'collateral_rating', 'collateral_residual_maturity', Account_no = F('account_no__account_no'), product_name = F('product__product_name'), product_code = F('product__product_code'), basel_collateral_code = F('collateral_code__basel_collateral_code'))

    items_list = defaultdict()

    for row in results:
        items_list[row["Account_no"]] = {"data":[], "bgcolor" : helpers.bg_color_codes()}

    for row in results:
        items_list[row["Account_no"]]["data"].append(row)

    print(items_list)

    #
    # DATA
    #==============================================================
    data["tab_status"] = None
    data["tab_active"] = 1
    data["content_template"] = 'administrator/show_collaterals.html'
    data["js_files"] = ['']
    data["sidebar_active"] = 3
    data["items_list"] = items_list

    return render(request, "administrator/index.html", data)

#**********************************************************************
# EDIT COLLATERAL
#**********************************************************************
def edit_collateral(request):
    pass


#**********************************************************************
# DELETE AUDIT TRAILS ALL
#**********************************************************************
def delete_audit_trails(request):
    Audit_Trail.objects.all().delete()
    messages.success(request, "Records Deleted Successfully")
    return HttpResponse(1)


#**********************************************************************
# DELETE AUDIT TRAILS SINGLE
#**********************************************************************
def delete_audit_trail_single(request):
    Audit_Trail.objects.get(pk=int(request.GET["id"])).delete()
    messages.success(request, "Records Deleted Successfully")
    return HttpResponse(1)



#**********************************************************************
# ENDPOINT: SHOW AUDIT TRAILS
#**********************************************************************
def show_audit_trail(request):

    data = defaultdict()

    audit_list = Audit_Trail.objects.all().select_related("user")

    data["items_list"] = defaultdict()
    data["content_template"] = "administrator/show_audit_trails.html"
    data["js_files"] = []
    data["sidebar_active"] = 6

    data["items_list"] = defaultdict()

    #
    #

    for row in audit_list:

        queryset = None
        options = None
        query_output = None
        all_opts = False

        #
        # EDITED
        #=========================================================
        if row.edited_data:
            bgc_color = "#fdf7a0"

            jdata = json.loads(row.edited_data_params)
            options = jdata["handler_table"]

            if row.parent not in ["master", "product", "collateral"]:
                if jdata["handler_table"] == "initial":
                    queryset = constants.TAB_ACTIVE[row.parent][3].select_related("account_no")
                    queryset = queryset.filter(id__in = jdata["selected_ids"]).values_list("account_no__account_no")
            else:
                if jdata["handler_table"] == "initial" and row.parent == "master":
                    queryset = constants.TAB_ACTIVE[row.parent][3].filter(id__in = jdata["selected_ids"]).values_list("account_no")

                    query_output = ', '.join([x[0] for x in queryset])

        #
        # MOVED
        #=========================================================
        if row.moved_data:
            bgc_color = "#d9f3bb"

            jdata = json.loads(row.moved_data_params)
            options = jdata["handler_table"]

            queryset = constants.TAB_ACTIVE[row.parent][4].select_related("account_no")
            queryset = queryset.filter(id__in = jdata["created_ids"]).values_list("account_no__account_no", "date")

            query_output = [{"date":x[1], "account_no":x[0]} for x in queryset]

        #
        # DELETED
        #=========================================================
        if row.deleted_data:
            bgc_color = "#f79c99"

            jdata = json.loads(row.deleted_data_params)
            options = jdata["handler_table"]

            #
            # COLLATERAL Mapping
            #=========================================================
            if row.parent == "collateral map":

                if len(jdata["selected_ids"]) > 0:
                    queryset = AccountMaster.objects.filter(id__in = jdata["selected_ids"]).values_list("account_no")
                    query_output = ', '.join([x[0] for x in queryset])

                    if "all" in jdata.keys():
                        if jdata["all"]:
                            query_output = "ALL FOR ACCOUNT : " + query_output
                        else:
                            query_output = "ONE RECORD FOR ACCOUNT : " + query_output
                else:
                    if "all" in jdata.keys():
                        if jdata["all"]:
                            all_opts = True



        #
        # REPORT RUN
        #=========================================================
        if row.report_run:
            bgc_color = "#f3c3ed"
            jdata = json.loads(row.report_run_params)

            #{"handler_table": "final", "start_date": null, "end_date": null, "account_no": null, "selected_ids": []}


            options = jdata["handler_table"]

            if len(jdata["selected_ids"]) > 0:
                queryset = constants.TAB_ACTIVE[row.parent][4].select_related("account_no")
                queryset = queryset.filter(id__in = jdata["selected_ids"]).values_list("account_no__account_no", "date")

                query_output = [{"date":x[1], "account_no":x[0]} for x in queryset]

            else:
                if "all" in jdata.keys():
                    if jdata["all"]:
                        all_opts = True

        #
        # REPORT DOWNLOAD
        #=========================================================
        if row.report_download:
            bgc_color = "#8072F8"


        main_data = {
            "date": row.date,
            "parent": row.parent,
            "edited_by": row.user.username,
            "edited_data": row.edited_data,
            "edit_params": query_output,
            "moved_data": row.moved_data,
            "moved_params": query_output,
            "deleted_data": row.deleted_data,
            "deleted_params": query_output,
            "report_run": row.report_run,
            "report_run_params": query_output,
            "report_download": row.report_download,
            "report_download_params": query_output,
            "bgcolor":bgc_color,
            "option":options,
            "all_opts": all_opts
        }

        data["items_list"][row.id]= main_data


    return render(request, "administrator/index.html", data)
