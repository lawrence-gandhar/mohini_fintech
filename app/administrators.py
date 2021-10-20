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
from django.db.models import F, Count, expressions

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
from collections import defaultdict




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
        ids = request.POST.getlist("ids",None)
        error_found = False
        error_count = 0

        users = New_User.objects.filter(pk__in = ids)

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

        users = New_User.objects.filter(pk__in = ids)

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

        New_User.objects.filter(pk__in = ids).delete()
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
        data["items_list"] = search_data(constants.TAB_ACTIVE[tab_status][3], request.POST)

    else:
        if tab_status != "master":
            data["items_list"] = constants.TAB_ACTIVE[tab_status][3].all().select_related("account_no")
        else:
            data["items_list"] = constants.TAB_ACTIVE[tab_status][3].all().order_by("account_no")
    #
    #
    data["items_list_json"] = helpers.queryset_row_to_json(data["items_list"])

    return render(request, "administrator/index.html", data)


#**********************************************************************
# Method to fetch data based on filters
# Can be done on initial and final datasets
# @model_obj: <model_name>.objects
# @form_data: request.POST or request.GET
#**********************************************************************
def search_data(model_obj = None, form_data = None):

    qry = None

    if model_obj is not None and form_data is not None:

        form_fields = form_data.keys()

        qry = model_obj
        #
        # Check & Fetch Account Number Parameter
        if "account_no" in form_fields:
            if form_data["account_no"].strip()!="":

                acc = list(AccountMaster.objects.filter(account_no__contains = form_data["account_no"]).values_list("id"))

                qry = qry.filter(account_no__in = acc)

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

        ts = calendar.timegm(time.gmtime())
        insert_data(data_set, import_type, ts)
        return redirect("manage_imports", import_type)
    return redirect("manage_imports")

#**********************************************************************
# METHOD TO INSERT DATA INTO RELEVANT MODELS
#**********************************************************************
def insert_data(data_set, import_type, file_identifier=None):

    for row in data_set:
        col_names = row.keys()

        #
        # MASTER ENTRY
        if import_type == "master":
            ins, created = AccountMaster.objects.update_or_create(
                date = row["date"] if row["date"].strip()!="" else None if "date" in col_names else None,
                cin = row["cin"] if row["cin"].strip()!="" else None if "cin" in col_names else None,
                account_no = row["account_no"] if row["account_no"].strip()!="" else None if "account_no" in col_names else None,
                account_type = row["account_type"] if row["account_type"].strip()!="" else None if "account_type" in col_names else None,
                product_name = row["product_name"] if row["product_name"].strip()!="" else None if "product_name" in col_names else None,
                sectors = row["sectors"] if row["sectors"].strip()!="" else None if "sectors" in col_names else None,
                customer_name = row["customer_name"] if row["customer_name"].strip()!="" else None if "customer_name" in col_names else None,
                contact_no = row["contact_no"] if row["contact_no"].strip()!="" else None if "contact_no" in col_names else None,
                email = row["email"] if row["email"].strip()!="" else None if "email" in col_names else None,
                pan = row["pan"] if row["pan"].strip()!="" else None if "pan" in col_names else None,
                aadhar_no = row["aadhar_no"] if row["aadhar_no"].strip()!="" else None if "aadhar_no" in col_names else None,
                customer_addr = row["customer_addr"] if row["customer_addr"].strip()!="" else None if "customer_addr" in col_names else None,
                pin = row["pin"] if row["pin"].strip()!="" else None if "pin" in col_names else None,
            )

        #
        # PD
        if import_type == "pd":

            ins, created = PD_Initial.objects.update_or_create(
             date = helpers.clean_data(row["date"]) if "date" in col_names else None,
             factor_1 = helpers.clean_data(row["factor_1"]) if "factor_1" in col_names else None,
             factor_2 = helpers.clean_data(row["factor_2"]) if "factor_2" in col_names else None,
             factor_3 = helpers.clean_data(row["factor_3"]) if "factor_3" in col_names else None,
             factor_4 = helpers.clean_data(row["factor_4"]) if "factor_4" in col_names else None,
             factor_5 = helpers.clean_data(row["factor_5"]) if "factor_5" in col_names else None,
             factor_6 = helpers.clean_data(row["factor_6"]) if "factor_6" in col_names else None,
             default_col = helpers.clean_data(row["default_col"]) if "default_col" in col_names else None,
             mgmt_overlay_1 = helpers.clean_data(row["mgmt_overlay_1"]) if "mgmt_overlay_1" in col_names else None,
             mgmt_overlay_2 = helpers.clean_data(row["mgmt_overlay_2"]) if "mgmt_overlay_2" in col_names else None,
            )

        #
        # LGD
        if import_type == "lgd":
            ins, created = LGD_Initial.objects.update_or_create(
             date = helpers.clean_data(row["date"]) if "date" in col_names else None,
             ead_os = helpers.clean_data(row["ead_os"]) if "ead_os" in col_names else None,
             pv_cashflows = helpers.clean_data(row["pv_cashflows"]) if "pv_cashflows" in col_names else None,
             pv_cost = helpers.clean_data(row["pv_cost"]) if "pv_cost" in col_names else None,
             beta_value = helpers.clean_data(row["beta_value"]) if "beta_value" in col_names else None,
             sec_flag = helpers.clean_data(row["sec_flag"]) if "sec_flag" in col_names else None,
             factor_4 = helpers.clean_data(row["factor_4"]) if "factor_4" in col_names else None,
             factor_5 = helpers.clean_data(row["factor_5"]) if "factor_5" in col_names else None,
             avg_1 = helpers.clean_data(row["avg_1"]) if "avg_1" in col_names else None,
             avg_2 = helpers.clean_data(row["avg_2"]) if "avg_2" in col_names else None,
             avg_3 = helpers.clean_data(row["avg_3"]) if "avg_3" in col_names else None,
             avg_4 = helpers.clean_data(row["avg_4"]) if "avg_4" in col_names else None,
             avg_5 = helpers.clean_data(row["avg_5"]) if "avg_5" in col_names else None,
             mgmt_overlay_1 = helpers.clean_data(row["mgmt_overlay_1"]) if "mgmt_overlay_1" in col_names else None,
             mgmt_overlay_2 = helpers.clean_data(row["mgmt_overlay_2"]) if "mgmt_overlay_2" in col_names else None,
            )

        #
        # STAGE
        if import_type == "stage":
            ins, created = Stage_Initial.objects.update_or_create(
             date = helpers.clean_data(row["date"]) if "date" in col_names else None,
             old_rating = helpers.clean_data(row["old_rating"]) if "old_rating" in col_names else None,
             new_rating = helpers.clean_data(row["new_rating"]) if "new_rating" in col_names else None,
             rating_3 = helpers.clean_data(row["rating_3"]) if "rating_3" in col_names else None,
             rating_4 = helpers.clean_data(row["rating_4"]) if "rating_4" in col_names else None,
             rating_5 = helpers.clean_data(row["rating_5"]) if "rating_5" in col_names else None,
             rating_6 = helpers.clean_data(row["rating_6"]) if "rating_6" in col_names else None,
             rating_7 = helpers.clean_data(row["rating_7"]) if "rating_7" in col_names else None,
             day_bucket_1 = helpers.clean_data(row["day_bucket_1"]) if "day_bucket_1" in col_names else None,
             day_bucket_2 = helpers.clean_data(row["day_bucket_2"]) if "day_bucket_2" in col_names else None,
             day_bucket_3 = helpers.clean_data(row["day_bucket_3"]) if "day_bucket_3" in col_names else None,
             day_bucket_4 = helpers.clean_data(row["day_bucket_4"]) if "day_bucket_4" in col_names else None,
             day_bucket_5 = helpers.clean_data(row["day_bucket_5"]) if "day_bucket_5" in col_names else None,
             day_bucket_6 = helpers.clean_data(row["day_bucket_6"]) if "day_bucket_6" in col_names else None,
             day_bucket_7 = helpers.clean_data(row["day_bucket_7"]) if "day_bucket_7" in col_names else None,
             day_bucket_8 = helpers.clean_data(row["day_bucket_8"]) if "day_bucket_8" in col_names else None,
             day_bucket_9 = helpers.clean_data(row["day_bucket_9"]) if "day_bucket_9" in col_names else None,
             day_bucket_10 = helpers.clean_data(row["day_bucket_10"]) if "day_bucket_10" in col_names else None,
             day_bucket_11 = helpers.clean_data(row["day_bucket_11"]) if "day_bucket_11" in col_names else None,
             day_bucket_12 = helpers.clean_data(row["day_bucket_12"]) if "day_bucket_12" in col_names else None,
             day_bucket_13 = helpers.clean_data(row["day_bucket_13"]) if "day_bucket_13" in col_names else None,
             day_bucket_14 = helpers.clean_data(row["day_bucket_14"]) if "day_bucket_14" in col_names else None,
             day_bucket_15 = helpers.clean_data(row["day_bucket_15"]) if "day_bucket_15" in col_names else None,
             criteria = helpers.clean_data(row["criteria"]) if "criteria" in col_names else None,
             cooling_period_1 = helpers.clean_data(row["cooling_period_1"]) if "cooling_period_1" in col_names else None,
             cooling_period_2 = helpers.clean_data(row["cooling_period_2"]) if "cooling_period_2" in col_names else None,
             cooling_period_3 = helpers.clean_data(row["cooling_period_3"]) if "cooling_period_3" in col_names else None,
             cooling_period_4 = helpers.clean_data(row["cooling_period_4"]) if "cooling_period_4" in col_names else None,
             cooling_period_5 = helpers.clean_data(row["cooling_period_5"]) if "cooling_period_5" in col_names else None,
             rbi_window = helpers.clean_data(row["rbi_window"]) if "rbi_window" in col_names else None,
             mgmt_overlay_1 = helpers.clean_data(row["mgmt_overlay_1"]) if "mgmt_overlay_1" in col_names else None,
             mgmt_overlay_2 = helpers.clean_data(row["mgmt_overlay_2"]) if "mgmt_overlay_2" in col_names else None,
            )

        #
        # Fetch Account Number Instance
        if "account_no" in col_names and import_type != "master":
            if row["account_no"].strip()!="":
                try:
                    account_ins = AccountMaster.objects.get(account_no = row["account_no"].strip())
                    ins.account_no = account_ins
                except ObjectDoesNotExist:
                    ins.account_no_temp = row["account_no"]
                    _, created = AccountMissing.objects.update_or_create(
                        account_no = row["account_no"],
                        file_identifier = file_identifier
                    )
        #
        # add file Identifier
        ins.file_identifier = file_identifier
        ins.save()


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
# METHOD TO EDIT DATA OF RELEVANT MODELS
#**********************************************************************
def edit_record(request, tab_status=None):
    if request.POST:

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
        try:
            account_ins = AccountMaster.objects.get(account_no = request.POST["account_no"])
            obj.account_no = account_ins
            obj.account_no_temp = None
            AccountMissing.objects.filter(account_no = request.POST["account_no"]).delete()
        except ObjectDoesNotExist:
            obj.account_no = None
            obj.account_no_temp = request.POST["account_no"]
            _, created = AccountMissing.objects.update_or_create(account_no = request.POST["account_no"])


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
        obj.edited_by = request.user
        obj.edited_on = timezone.now()

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
        record_failed = False

        if len(ids) == 0:
            messages.error(request, "Operation Failed. No records selected")
            return redirect("manage_imports", tab_status)

        for id in ids:
            try:
                obj = constants.TAB_ACTIVE[tab_status][3].get(pk = id)

                if obj.account_no is None:
                    no_account = True
                else:
                    if move_record(tab_status, obj):
                        record_failed = True

            except ObjectDoesNotExist:
                not_found = True

        #
        #
        if not_found:
            messages.error(request, "Operation Failed. One/Multiple records not Found. Failed to Move data.")
            return redirect("manage_imports", tab_status)
        elif no_account or record_failed:
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

        if move_record(tab_status, obj):
            messages.success(request, "Record Moved Successfully")
        else:
            messages.error(request, "Operation Failed.")
    else:
        messages.error(request, "Operation Failed.")
    return redirect("manage_imports", tab_status)


#**********************************************************************
# PRIVATE METHOD TO MOVE RECORD:
# USED IN @move_to_final and @move_all_to_final
# @obj is the instance of the queryset
#**********************************************************************
def move_record(tab_status=None, obj=None):

    if tab_status == "pd" and obj is not None:
        constants.TAB_ACTIVE[tab_status][4].create(
            date = obj.date,
            account_no = obj.account_no,
            factor_1 = obj.factor_1,
            factor_2 = obj.factor_2,
            factor_3 = obj.factor_3,
            factor_4 = obj.factor_4,
            factor_5 = obj.factor_5,
            factor_6 = obj.factor_6,
            default_col = obj.default_col,
            mgmt_overlay_1 = obj.mgmt_overlay_1,
            mgmt_overlay_2 = obj.mgmt_overlay_2,
        )

        obj.delete()
        return True

    elif tab_status == "lgd" and obj is not None:
        constants.TAB_ACTIVE[tab_status][4].create(
            date = obj.date,
            account_no = obj.account_no,
            ead_os = obj.ead_os,
            pv_cashflows = obj.pv_cashflows,
            pv_cost = obj.pv_cost,
            beta_value = obj.beta_value,
            sec_flag = obj.sec_flag,
            factor_4 = obj.factor_4,
            factor_5 = obj.factor_5,
            avg_1 = obj.avg_1,
            avg_2 = obj.avg_2,
            avg_3 = obj.avg_3,
            avg_4 = obj.avg_4,
            avg_5 = obj.avg_5,
            mgmt_overlay_1 = obj.mgmt_overlay_1,
            mgmt_overlay_2 = obj.mgmt_overlay_2,
        )

        obj.delete()
        return True

    elif tab_status == "stage" and obj is not None:
        constants.TAB_ACTIVE[tab_status][4].create(
            date = obj.date,
            account_no = obj.account_no,
            old_rating = obj.old_rating,
            new_rating = obj.new_rating,
            rating_3 = obj.rating_3,
            rating_4 = obj.rating_4,
            rating_5 = obj.rating_5,
            rating_6 = obj.rating_6,
            rating_7 = obj.rating_7,
            day_bucket_1 = obj.day_bucket_1,
            day_bucket_2 = obj.day_bucket_2,
            day_bucket_3 = obj.day_bucket_3,
            day_bucket_4 = obj.day_bucket_4,
            day_bucket_5 = obj.day_bucket_5,
            day_bucket_6 = obj.day_bucket_6,
            day_bucket_7 = obj.day_bucket_7,
            day_bucket_8 = obj.day_bucket_8,
            day_bucket_9 = obj.day_bucket_9,
            day_bucket_10 = obj.day_bucket_10,
            day_bucket_11 = obj.day_bucket_11,
            day_bucket_12 = obj.day_bucket_12,
            day_bucket_13 = obj.day_bucket_13,
            day_bucket_14 = obj.day_bucket_14,
            day_bucket_15 = obj.day_bucket_15,
            criteria = obj.criteria,
            cooling_period_1 = obj.cooling_period_1,
            cooling_period_2 = obj.cooling_period_2,
            cooling_period_3 = obj.cooling_period_3,
            cooling_period_4 = obj.cooling_period_4,
            cooling_period_5 = obj.cooling_period_5,
            rbi_window = obj.rbi_window,
            mgmt_overlay_1 = obj.mgmt_overlay_1,
            mgmt_overlay_2 = obj.mgmt_overlay_2
        )

        obj.delete()
        return True
    else:
        return False


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
        results = constants.TAB_ACTIVE[tab_status][4].select_related("account_no")
        results = results.values('id', 'date', 'account_no_id', 'factor_1', 'factor_2', 'factor_3', 'factor_4', 'default_col', 'factor_5', 'factor_6', 'mgmt_overlay_1', 'mgmt_overlay_2', Account_No = F('account_no__account_no'), cin = F('account_no__cin'), product_name = F('account_no__product_name'), sectors = F('account_no__sectors'), account_type = F('account_no__account_type'))



    #
    # TAB- LGD
    #==============================================================
    if tab_status == "lgd":
        results = constants.TAB_ACTIVE[tab_status][4].select_related("account_no")
        results = results.values('id', 'date', 'account_no_id', 'ead_os', 'pv_cashflows', 'pv_cost', 'beta_value', 'sec_flag', 'factor_4', 'factor_5', 'avg_1', 'avg_2', 'avg_3', 'avg_4', 'avg_5', 'mgmt_overlay_1', 'mgmt_overlay_2', Account_No = F('account_no__account_no'), cin = F('account_no__cin'), product_name = F('account_no__product_name'), sectors = F('account_no__sectors'), account_type = F('account_no__account_type')).order_by("id")

    #
    # TAB- Stage
    #==============================================================
    if tab_status == "stage":
        results = constants.TAB_ACTIVE[tab_status][4].select_related("account_no")
        results.values('id', 'date', 'account_no_id', 'old_rating', 'new_rating', 'rating_3', 'rating_4', 'rating_5', 'rating_6', 'rating_7', 'day_bucket_1', 'day_bucket_2', 'day_bucket_3', 'day_bucket_4', 'day_bucket_5', 'day_bucket_6', 'day_bucket_7', 'day_bucket_8', 'day_bucket_9', 'day_bucket_10', 'day_bucket_11', 'day_bucket_12','day_bucket_13', 'day_bucket_14', 'day_bucket_15', 'criteria', 'cooling_period_1', 'cooling_period_2', 'cooling_period_3', 'cooling_period_4', 'cooling_period_5', 'rbi_window', 'mgmt_overlay_1', 'mgmt_overlay_2', Account_No = F('account_no__account_no'), cin = F('account_no__cin'), product_name = F('account_no__product_name'), sectors = F('account_no__sectors'), account_type = F('account_no__account_type')).order_by("id")

    #
    # PAGINATIONS
    #==============================================================

    results = results.order_by("id")

    page = request.GET.get('page', 1)

    paginator = Paginator(results, 10)
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)

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

def pd_report(request):

    ret = False
    start_date = request.POST["start_date"] if request.POST["start_date"].strip()!="" else None
    end_date = request.POST["end_date"] if request.POST["end_date"].strip()!="" else None
    account_no = [helpers.clean_data(x) for x in request.POST["account_no"].split(",")] if request.POST["account_no"].strip()!="" else None
    id_selected = request.POST.getlist("checkbox_one", None)

    ret = background_tasks.pd_report(start_date = start_date, end_date = end_date, account_no = account_no)
    if ret:

        results = PD_Report.objects

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

        results = results.select_related('account_no').values('id','date', 'account_no__account_no', 'account_type', 'cin', 'product_name', 'sectors', 'factor_1', 'factor_2', 'factor_3', 'factor_4', 'factor_5', 'factor_6', 'default_col', 'mgmt_overlay_1', 'mgmt_overlay_2', 'intercept', 'coeff_fact1', 'coeff_fact2', 'coeff_fact3', 'coeff_fact4', 'zscore', 'pd')

    if request.is_ajax():
        if ret:
            return JsonResponse({"ret":ret, "msg":"PD Report Created Successfully", "results":list(results)})
        else:
            return JsonResponse({"ret":ret, "msg":"PD Report Creation Failed"})
    else:
        rev = reverse("show_reports")

        params = request.POST.urlencode()
        rev = '{}?{}'.format(rev, params)
        return redirect(rev)


#**********************************************************************
# ENDPOINT: GENERATE REPORT - LGD
#**********************************************************************
def lgd_report(request):

    ret = False
    start_date = request.POST["start_date"] if request.POST["start_date"].strip()!="" else None
    end_date = request.POST["end_date"] if request.POST["end_date"].strip()!="" else None
    account_no = [helpers.clean_data(x) for x in request.POST["account_no"].split(",")] if request.POST["account_no"].strip()!="" else None
    id_selected = request.POST.getlist("checkbox_one", None)

    ret = background_tasks.lgd_report(start_date = start_date, end_date = end_date, account_no = account_no)
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

        results = results.select_related('account_no').values('id','date', 'account_no__account_no', 'account_type', 'cin', 'product_name', 'sectors', 'ead_os', 'pv_cost', 'pv_cashflows', 'beta_value', 'sec_flag', 'factor_4', 'factor_5', 'avg_1', 'avg_2', 'avg_3', 'avg_4', 'avg_5', 'mgmt_overlay_1', 'mgmt_overlay_2',
        'rec_rate', 'est_rr', 'est_lgd', 'final_lgd')

    if request.is_ajax():
        if ret:
            return JsonResponse({"ret":ret, "msg":"LGD Report Created Successfully", "results":list(results)})
        else:
            return JsonResponse({"ret":ret, "msg":"LGD Report Creation Failed"})
    else:
        return redirect("show_reports", "lgd")


#**********************************************************************
# ENDPOINT: GENERATE REPORT - STAGE
#**********************************************************************
def stage_report(request):

    ret = False
    start_date = request.POST["start_date"] if request.POST["start_date"].strip()!="" else None
    end_date = request.POST["end_date"] if request.POST["end_date"].strip()!="" else None
    account_no = [helpers.clean_data(x) for x in request.POST["account_no"].split(",")] if request.POST["account_no"].strip()!="" else None
    id_selected = request.POST.getlist("checkbox_one", None)

    ret = background_tasks.stage_report(start_date = start_date, end_date = end_date, account_no = account_no)
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

        results = results.select_related('account_no').values('id', 'date', 'account_no__account_no', 'account_type', 'cin', 'product_name', 'sectors', 'stage', 'state', 'old_rating', 'new_rating', 'rating_3', 'rating_4', 'rating_5', 'rating_6', 'rating_7', 'day_bucket_1', 'day_bucket_2', 'day_bucket_3', 'day_bucket_4', 'day_bucket_5', 'day_bucket_6', 'day_bucket_7', 'day_bucket_8', 'day_bucket_9', 'day_bucket_10', 'day_bucket_11', 'day_bucket_12', 'day_bucket_13', 'day_bucket_14', 'day_bucket_15', 'criteria', 'cooling_period_1', 'cooling_period_2', 'cooling_period_3', 'cooling_period_4', 'cooling_period_5', 'rbi_window', 'mgmt_overlay_1', 'mgmt_overlay_2')

    if request.is_ajax():
        if ret:
            return JsonResponse({"ret":ret, "msg":"Stage Report Created Successfully", "results":list(results)})
        else:
            return JsonResponse({"ret":ret, "msg":"Stage Report Creation Failed"})
    else:
        return redirect("show_reports", "stage")



#**********************************************************************
# ENDPOINT: REPORT - SHOW
#**********************************************************************
def show_reports(request, tab_status=None):

    data = defaultdict()

    if tab_status is None:
        tab_status = "pd"

    #
    # GET REQUESTS
    #==============================================================
    start_date = request.GET.get("start_date").strip() if request.GET.get("start_date") else None
    end_date = request.GET.get("end_date").strip() if request.GET.get("end_date") else None
    account_no = [helpers.clean_data(x) for x in request.GET.get("account_no").strip().split(",")] if request.GET.get("account_no") else None

    #
    # TAB- PD
    #==============================================================
    if tab_status == "pd":
        results = PD_Report.objects

        if start_date is None and end_date is None and account_no is None:
            results = results.all()

        if start_date is not None:
            if end_date is not None:
                results = results.filter(date__gte = start_date, date__lte = end_date)
            else:
                results = results.filter(date__gte = start_date)

        if account_no is not None:
            results = results.filter(account_no__account_no__in = account_no)

        results = results.select_related('account_no').values('id', 'date', 'account_no__account_no', 'account_type', 'cin', 'product_name', 'sectors', 'factor_1', 'factor_2', 'factor_3', 'factor_4', 'factor_5', 'factor_6', 'default_col', 'mgmt_overlay_1', 'mgmt_overlay_2', 'intercept', 'coeff_fact1', 'coeff_fact2', 'coeff_fact3', 'coeff_fact4', 'zscore', 'pd').order_by("id")

    #
    # TAB- LGD
    #==============================================================
    if tab_status == "lgd":
        results = LGD_Report.objects

        if start_date is None and end_date is None and account_no is None:
            results = results.all()

        if start_date is not None:
            if end_date is not None:
                results = results.filter(date__gte = start_date, date__lte = end_date)
            else:
                results = results.filter(date__gte = start_date)

        if account_no is not None:
            results = results.filter(account_no__account_no__in = account_no)

        results = results.select_related('account_no').values('id', 'date', 'account_no__account_no', 'account_type', 'cin', 'product_name', 'sectors', 'ead_os', 'pv_cashflows', 'pv_cost', 'beta_value', 'factor_5', 'sec_flag', 'factor_4', 'factor_5', 'avg_1', 'avg_2', 'avg_3', 'avg_4', 'avg_5', 'mgmt_overlay_2', 'rec_rate', 'est_rr', 'est_lgd', 'final_lgd').order_by("id")


    #
    # TAB- STAGE
    #==============================================================
    if tab_status == "stage":
        results = Stage_Report.objects

        if start_date is None and end_date is None and account_no is None:
            results = results.all()

        if start_date is not None:
            if end_date is not None:
                results = results.filter(date__gte = start_date, date__lte = end_date)
            else:
                results = results.filter(date__gte = start_date)

        if account_no is not None:
            results = results.filter(account_no__account_no__in = account_no)

        results = results.select_related('account_no').values('id' ,'date', 'account_no__account_no', 'account_type', 'cin', 'product_name', 'sectors', 'stage', 'state', 'old_rating', 'new_rating', 'rating_3', 'rating_4', 'rating_5', 'rating_6', 'rating_7', 'day_bucket_1', 'day_bucket_2', 'day_bucket_3', 'day_bucket_4', 'day_bucket_5', 'day_bucket_6', 'day_bucket_7', 'day_bucket_8', 'day_bucket_9', 'day_bucket_10', 'day_bucket_11', 'day_bucket_12', 'day_bucket_13', 'day_bucket_14', 'day_bucket_15', 'criteria', 'cooling_period_1', 'cooling_period_2', 'cooling_period_3', 'cooling_period_4', 'cooling_period_5', 'rbi_window', 'mgmt_overlay_1', 'mgmt_overlay_2').order_by("id")

    #
    # PAGINATIONS
    #==============================================================
    page = request.GET.get('page', 1)

    paginator = Paginator(results, 2)
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)

    #
    # DATA
    #==============================================================
    data["tab_status"] = tab_status
    data["tab_active"] = constants.TAB_ACTIVE[tab_status][0]
    data["content_template"] = constants.TAB_ACTIVE[tab_status][8]
    data["js_files"] = []
    data["sidebar_active"] = 7
    data["items_list"] = results

    return render(request, "administrator/index.html", data)
