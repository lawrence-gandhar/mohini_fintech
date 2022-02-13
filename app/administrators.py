#
# AUTHOR : LAWRENCE GANDHAR
# Project For Mohini - (India)
# Project Date : 14th Sept 2021
#

from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages

from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

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

import pandas as pd
from django.conf import settings



#**********************************************************************
# ENDPOINT: DASHBOARD - ADMIN
#**********************************************************************
def user_dashboard(request):
    data = defaultdict()
    data["sidebar_active"] = 1
    data["content_template"] = "administrator/dashboard.html"

    #
    #
    #===================================================================
    qry = """
        select sum(WS.ead_total) as id, sum(WS.final_ecl) as final_ecl_sum from (select ECL.tenure, PD.pd, LGD.final_lgd, EAD.ead_total, ECL.final_ecl
        from app_ecl_reports ECL
        left join app_pd_report PD on PD.account_no_id = ECL.account_no_id and PD.date = ECL.date
        left join app_lgd_report LGD on LGD.account_no_id = ECL.account_no_id and LGD.date = ECL.date
        left join app_stage_report ST on ST.account_no_id = ECL.account_no_id and ST.date = ECL.date
        left join app_ead_report EAD on EAD.account_no_id = ECL.account_no_id and EAD.date = ECL.date) WS
    """

    ead_total = constants.TAB_ACTIVE["ecl"][9].raw(qry)

    ead_total_sum = 0
    final_ecl_sum = 0

    for row in ead_total:
        ead_total_sum = row.id if row.id is not None else 0
        final_ecl_sum = row.final_ecl_sum if row.final_ecl_sum is not None else 0

    data["ead_total_sum"] = round(ead_total_sum)
    data["final_ecl_sum"] = round(final_ecl_sum)


    #
    #
    #====================================================================

    sector_data_qry = constants.TAB_ACTIVE["ecl"][9].raw("""
        select 1 as id, DS.sectors as sector, sum(DS.final_ecl) as final_ecl, sum(DS.ead_total) as ead_total from (
        select ECL.final_ecl, EAD.ead_total, AC.sectors from app_ecl_reports ECL
        inner join app_accountmaster AC on ECL.account_no_id = AC.id
        inner join app_ead_report EAD on EAD.account_no_id = ECL.account_no_id
        ) DS group by DS.sectors
    """)


    sector_chart_data = [['x'],['ECL'],['EAD']]

    for row in sector_data_qry:
        sector_chart_data[0].append(row.sector)
        sector_chart_data[1].append(round(row.ead_total))
        sector_chart_data[2].append(round(row.final_ecl))

    data["sector_chart_data"] = sector_chart_data

    #
    #
    #====================================================================

    stage_data_qry = constants.TAB_ACTIVE["ecl"][9].raw("""
        select 1 as id, DS.stage as stage, sum(DS.final_ecl) as final_ecl from (
        select ECL.final_ecl, ST.stage  from app_ecl_reports ECL
        inner join app_accountmaster AC on ECL.account_no_id = AC.id
        inner join app_stage_report ST on ST.account_no_id = ECL.account_no_id
        ) DS group by DS.stage
    """)

    stage_chart_data = []

    total_ecl = 0
    for row in stage_data_qry:
        total_ecl += abs(round(row.final_ecl))

    for row in stage_data_qry:
        stage_chart_data.append(['STAGE {}'.format(row.stage), round((abs(row.final_ecl)/total_ecl)*100)])

    data["stage_chart_data"] = stage_chart_data


    #
    #
    #====================================================================

    product_data_qry = constants.TAB_ACTIVE["ecl"][9].raw("""
        select 1 as id, DS.product_code, DS.product_name, sum(DS.final_ecl) as final_ecl, sum(DS.ead_total) as ead_total from (
        select ECL.final_ecl, EAD.ead_total, BP.product_code, BP.product_name from app_ecl_reports ECL
        inner join app_collateral AC on ECL.account_no_id = AC.account_no_id
        inner join app_basel_product_master BP on BP.id = AC.product_id
        inner join app_ead_report EAD on EAD.account_no_id = ECL.account_no_id
        ) DS group by DS.product_name
    """)

    product_chart_data = [['x'],['ECL'],['EAD']]

    for row in product_data_qry:
        product_chart_data[0].append(row.product_name)
        product_chart_data[1].append(round(row.ead_total))
        product_chart_data[2].append(round(row.final_ecl))

    data["product_chart_data"] = product_chart_data

    return render(request, "administrator/index.html", data)


#**********************************************************************
# ENDPOINT: DASHBOARD - ADMIN
#**********************************************************************
def dashboard(request):
    data = defaultdict()
    data["sidebar_active"] = 1
    data["content_template"] = "administrator/dashboard.html"

    #
    #
    #===================================================================
    qry = """
        select sum(WS.ead_total) as id, sum(WS.final_ecl) as final_ecl_sum from (select ECL.tenure, PD.pd, LGD.final_lgd, EAD.ead_total, ECL.final_ecl
        from app_ecl_reports ECL
        left join app_pd_report PD on PD.account_no_id = ECL.account_no_id and PD.date = ECL.date
        left join app_lgd_report LGD on LGD.account_no_id = ECL.account_no_id and LGD.date = ECL.date
        left join app_stage_report ST on ST.account_no_id = ECL.account_no_id and ST.date = ECL.date
        left join app_ead_report EAD on EAD.account_no_id = ECL.account_no_id and EAD.date = ECL.date) WS
    """

    ead_total = constants.TAB_ACTIVE["ecl"][9].raw(qry)

    ead_total_sum = 0
    final_ecl_sum = 0

    for row in ead_total:
        ead_total_sum = row.id if row.id is not None else 0
        final_ecl_sum = row.final_ecl_sum if row.final_ecl_sum is not None else 0

    data["ead_total_sum"] = round(ead_total_sum)
    data["final_ecl_sum"] = round(final_ecl_sum)


    #
    #
    #====================================================================

    sector_data_qry = constants.TAB_ACTIVE["ecl"][9].raw("""
        select 1 as id, DS.sectors as sector, sum(DS.final_ecl) as final_ecl, sum(DS.ead_total) as ead_total from (
        select ECL.final_ecl, EAD.ead_total, AC.sectors from app_ecl_reports ECL
        inner join app_accountmaster AC on ECL.account_no_id = AC.id
        inner join app_ead_report EAD on EAD.account_no_id = ECL.account_no_id
        ) DS group by DS.sectors
    """)


    sector_chart_data = [['x'],['EAD'],['ECL']]

    for row in sector_data_qry:
        sector_chart_data[0].append(row.sector)
        sector_chart_data[1].append(round(row.ead_total))
        sector_chart_data[2].append(round(row.final_ecl))

    data["sector_chart_data"] = sector_chart_data

    #
    #
    #====================================================================

    stage_data_qry = constants.TAB_ACTIVE["ecl"][9].raw("""
        select 1 as id, DS.stage as stage, sum(DS.final_ecl) as final_ecl from (
        select ECL.final_ecl, ST.stage  from app_ecl_reports ECL
        inner join app_accountmaster AC on ECL.account_no_id = AC.id
        inner join app_stage_report ST on ST.account_no_id = ECL.account_no_id
        ) DS group by DS.stage
    """)

    stage_chart_data = []

    total_ecl = 0

    for row in stage_data_qry:
        total_ecl += abs(round(row.final_ecl))

    for row in stage_data_qry:
        stage_chart_data.append(['STAGE {}'.format(row.stage), round((abs(row.final_ecl)/total_ecl)*100)])

    data["stage_chart_data"] = stage_chart_data


    #
    #
    #====================================================================

    product_data_qry = constants.TAB_ACTIVE["ecl"][9].raw("""
        select 1 as id, DS.product_code, DS.product_name, sum(DS.final_ecl) as final_ecl, sum(DS.ead_total) as ead_total from (
        select ECL.final_ecl, EAD.ead_total, BP.product_code, BP.product_name from app_ecl_reports ECL
        inner join app_collateral AC on ECL.account_no_id = AC.account_no_id
        inner join app_basel_product_master BP on BP.id = AC.product_id
        inner join app_ead_report EAD on EAD.account_no_id = ECL.account_no_id
        ) DS group by DS.product_name
    """)

    product_chart_data = [['x'],['EAD'],['ECL']]

    for row in product_data_qry:
        product_chart_data[0].append(row.product_name)
        product_chart_data[1].append(round(row.ead_total))
        product_chart_data[2].append(round(row.final_ecl))

    data["product_chart_data"] = product_chart_data

    return render(request, "administrator/index.html", data)


#**********************************************************************
# ENDPOINT: MANAGE USERS
#**********************************************************************
def manage_users(request):

    data = defaultdict()
    data["content_template"] = "administrator/manage_users.html"
    data["js_files"] = ['custom_js/admin.js']
    data["add_user_form"] = CreateUserForm(auto_id = "add_form_%s")
    data["edit_user_form"] = EditUserForm(auto_id = "edit_%s")

    data["model_show"] = False
    data["sidebar_active"] = 2

    main_qry = """
    select U.id, U.username, U.email, U.first_name, U.last_name, U.is_staff, U.is_superuser, AM.upload_master_table, AM.edit_master_table, AM.delete_master_table, AM.upload_basel_product, AM.edit_basel_product, AM.delete_basel_product, AM.upload_basel_collateral, AM.edit_basel_collateral, AM.delete_basel_collateral, AM.upload_collateral_mapper, AM.edit_collateral_mapper, AM.delete_collateral_mapper, AM.upload_pd, AM.upload_lgd, AM.upload_ead, AM.upload_ecl, AM.upload_eir, AM.upload_stage, AM.edit_import_pd, AM.edit_import_lgd, AM.edit_import_ead, AM.edit_import_ecl, AM.edit_import_eir, AM.edit_import_stage, AM.delete_import_pd, AM.delete_import_lgd, AM.delete_import_ead, AM.delete_import_ecl, AM.delete_import_eir, AM.delete_import_stage, AM.edit_final_pd, AM.edit_final_lgd, AM.edit_final_ead, AM.edit_final_ecl, AM.edit_final_eir, AM.edit_final_stage, AM.delete_final_pd, AM.delete_final_lgd, AM.delete_final_ead, AM.delete_final_ecl, AM.delete_final_eir, AM.delete_final_stage, AM.run_final_pd, AM.run_final_lgd, AM.run_final_ead, AM.run_final_ecl, AM.run_final_eir, AM.run_final_stage,
    AM.download_reports_pd, AM.download_reports_lgd, AM.download_reports_ead, AM.download_reports_ecl, AM.download_reports_eir, AM.download_reports_stage from auth_user U left join app_accessmanage AM on U.id = AM.user_id
    """

    data["users"] = User.objects.raw(main_qry)

    data["users_json"] = {}

    for row in data["users"]:
        try:
            data["users_json"][row.id] = {
                "username" : row.username,
                "email" : row.email,
                "first_name" : row.first_name,
                "last_name" : row.last_name,
                "is_staff" : row.is_staff,
                "is_superuser" : row.is_superuser,
                "upload_master_table" : bool(row.upload_master_table),
                "edit_master_table" : bool(row.edit_master_table),
                "delete_master_table" : bool(row.delete_master_table),
                "upload_basel_product" : bool(row.upload_basel_product),
                "edit_basel_product" : bool(row.edit_basel_product),
                "delete_basel_product" : bool(row.delete_basel_product),
                "upload_basel_collateral" : bool(row.upload_basel_collateral),
                "edit_basel_collateral" : bool(row.edit_basel_collateral),
                "delete_basel_collateral" : bool(row.delete_basel_collateral),
                "upload_collateral_mapper" : bool(row.upload_collateral_mapper),
                "edit_collateral_mapper" : bool(row.edit_collateral_mapper),
                "delete_collateral_mapper" : bool(row.delete_collateral_mapper),
                "upload_pd" : bool(row.upload_pd),
                "upload_lgd" : bool(row.upload_lgd),
                "upload_ead" : bool(row.upload_ead),
                "upload_ecl" : bool(row.upload_ecl),
                "upload_eir" : bool(row.upload_eir),
                "upload_stage" : bool(row.upload_stage),
                "edit_import_pd" : bool(row.edit_import_pd),
                "edit_import_lgd" : bool(row.edit_import_lgd),
                "edit_import_ead" : bool(row.edit_import_ead),
                "edit_import_ecl" : bool(row.edit_import_ecl),
                "edit_import_eir" : bool(row.edit_import_eir),
                "edit_import_stage" : bool(row.edit_import_stage),
                "delete_import_pd" : bool(row.delete_import_pd),
                "delete_import_lgd" : bool(row.delete_import_lgd),
                "delete_import_stage" : bool(row.delete_import_stage),
                "delete_import_eir" : bool(row.delete_import_eir),
                "delete_import_ecl" : bool(row.delete_import_ecl),
                "edit_final_pd" : bool(row.edit_final_pd),
                "edit_final_lgd" : bool(row.edit_final_lgd),
                "edit_final_stage" : bool(row.edit_final_stage),
                "edit_final_eir" : bool(row.edit_final_eir),
                "edit_final_ecl" : bool(row.edit_final_ecl),
                "delete_final_pd" : bool(row.delete_final_pd),
                "delete_final_lgd" : bool(row.delete_final_lgd),
                "delete_final_stage" : bool(row.delete_final_stage),
                "delete_final_eir" : bool(row.delete_final_eir),
                "delete_final_ecl" : bool(row.delete_final_ecl),
                "run_final_pd" : bool(row.run_final_pd),
                "run_final_lgd" : bool(row.run_final_lgd),
                "run_final_stage" : bool(row.run_final_stage),
                "run_final_eir" : bool(row.run_final_eir),
                "run_final_ecl" : bool(row.run_final_ecl),
                "download_reports_pd" : bool(row.download_reports_pd),
                "download_reports_lgd" : bool(row.download_reports_lgd),
                "download_reports_stage" : bool(row.download_reports_stage),
                "download_reports_eir" : bool(row.download_reports_eir),
                "download_reports_ecl" : bool(row.download_reports_ecl),
            }
        except KeyError:
            data["users_json"] = {
                "username" : row.username,
                "email" : row.email,
                "first_name" : row.first_name,
                "last_name" : row.last_name,
                "is_staff" : row.is_staff,
                "is_superuser" : row.is_superuser,
                "upload_master_table" : bool(row.upload_master_table),
                "edit_master_table" : bool(row.edit_master_table),
                "delete_master_table" : bool(row.delete_master_table),
                "upload_basel_product" : bool(row.upload_basel_product),
                "edit_basel_product" : bool(row.edit_basel_product),
                "delete_basel_product" : bool(row.delete_basel_product),
                "upload_basel_collateral" : bool(row.upload_basel_collateral),
                "edit_basel_collateral" : bool(row.edit_basel_collateral),
                "delete_basel_collateral" : bool(row.delete_basel_collateral),
                "upload_collateral_mapper" : bool(row.upload_collateral_mapper),
                "edit_collateral_mapper" : bool(row.edit_collateral_mapper),
                "delete_collateral_mapper" : bool(row.delete_collateral_mapper),
                "upload_pd" : bool(row.upload_pd),
                "upload_lgd" : bool(row.upload_lgd),
                "upload_ead" : bool(row.upload_ead),
                "upload_ecl" : bool(row.upload_ecl),
                "upload_eir" : bool(row.upload_eir),
                "upload_stage" : bool(row.upload_stage),
                "edit_import_pd" : bool(row.edit_import_pd),
                "edit_import_lgd" : bool(row.edit_import_lgd),
                "edit_import_ead" : bool(row.edit_import_ead),
                "edit_import_ecl" : bool(row.edit_import_ecl),
                "edit_import_eir" : bool(row.edit_import_eir),
                "edit_import_stage" : bool(row.edit_import_stage),
                "delete_import_pd" : bool(row.delete_import_pd),
                "delete_import_lgd" : bool(row.delete_import_lgd),
                "delete_import_stage" : bool(row.delete_import_stage),
                "delete_import_eir" : bool(row.delete_import_eir),
                "delete_import_ecl" : bool(row.delete_import_ecl),
                "edit_final_pd" : bool(row.edit_final_pd),
                "edit_final_lgd" : bool(row.edit_final_lgd),
                "edit_final_stage" : bool(row.edit_final_stage),
                "edit_final_eir" : bool(row.edit_final_eir),
                "edit_final_ecl" : bool(row.edit_final_ecl),
                "delete_final_pd" : bool(row.delete_final_pd),
                "delete_final_lgd" : bool(row.delete_final_lgd),
                "delete_final_stage" : bool(row.delete_final_stage),
                "delete_final_eir" : bool(row.delete_final_eir),
                "delete_final_ecl" : bool(row.delete_final_ecl),
                "run_final_pd" : bool(row.run_final_pd),
                "run_final_lgd" : bool(row.run_final_lgd),
                "run_final_stage" : bool(row.run_final_stage),
                "run_final_eir" : bool(row.run_final_eir),
                "run_final_ecl" : bool(row.run_final_ecl),
                "download_reports_pd" : bool(row.download_reports_pd),
                "download_reports_lgd" : bool(row.download_reports_lgd),
                "download_reports_stage" : bool(row.download_reports_stage),
                "download_reports_eir" : bool(row.download_reports_eir),
                "download_reports_ecl" : bool(row.download_reports_ecl),
            }


    data["users_json"] = json.dumps(data["users_json"])

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
    data["js_files"] = ['custom_js/imports.js?version=1.1']
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


        #
        #
        if tab_status == "eir":
            obj.date = request.POST["date"] if request.POST["date"].strip()!="" else None
            obj.period = request.POST["period"] if request.POST["period"].strip()!="" else None
            obj.loan_availed = request.POST["loan_availed"] if request.POST["loan_availed"].strip()!="" else None
            obj.cost_avail = request.POST["cost_avail"] if request.POST["cost_avail"].strip()!="" else None
            obj.rate = request.POST["rate"] if request.POST["rate"].strip()!="" else None
            obj.emi = request.POST["emi"] if request.POST["emi"].strip()!="" else None
            obj.os_principal = request.POST["os_principal"] if request.POST["os_principal"].strip()!="" else None
            obj.os_interest = request.POST["os_interest"] if request.POST["os_interest"].strip()!="" else None
            obj.fair_value = request.POST["fair_value"] if request.POST["fair_value"].strip()!="" else None
            obj.coupon = request.POST["coupon"] if request.POST["coupon"].strip()!="" else None
            obj.discount_factor = request.POST["discount_factor"] if request.POST["discount_factor"].strip()!="" else None
            obj.col_1 = request.POST["col_1"] if request.POST["col_1"].strip()!="" else None
            obj.col_2 = request.POST["col_2"] if request.POST["col_2"].strip()!="" else None
            obj.col_3 = request.POST["col_3"] if request.POST["col_3"].strip()!="" else None
            obj.default_eir = request.POST["default_eir"] if request.POST["default_eir"].strip()!="" else None
            obj.default_eir = request.POST["default_eir"] if request.POST["default_eir"].strip()!="" else None

        #
        #
        if tab_status == "ecl":
            obj.date = request.POST["date"] if request.POST["date"].strip()!="" else None
            obj.tenure = request.POST["tenure"] if request.POST["tenure"].strip()!="" else None

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


    account_no_search = request.GET.get('account_no')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    acc_no_ins = None

    if account_no_search is not None:
        if account_no_search !="":
            acc_no_ins = AccountMaster.objects.filter(account_no__icontains = account_no_search)


    #
    # TAB- PD
    #==============================================================
    if tab_status == "pd":
        product_qry = """select product_name from app_basel_product_master where id = (select distinct(product_id) from app_collateral where account_no_id = app_pd_final.account_no_id)"""

        results = constants.TAB_ACTIVE[tab_status][4].extra(select={'product_name': product_qry}).select_related("account_no")

        if acc_no_ins is not None:
            results = results.filter(account_no__in = acc_no_ins)

        if start_date is not None:
            if start_date !="":
                results = results.filter(date__gte = start_date)

        if end_date is not None:
            if end_date !="":
                results = results.filter(date__lte = end_date)

        results = results.values('id', 'date', 'account_no_id', 'product_name', 'factor_1', 'factor_2', 'factor_3', 'factor_4', 'default_col', 'factor_5', 'factor_6', 'mgmt_overlay_1', 'mgmt_overlay_2', Account_No = F('account_no__account_no'), cin = F('account_no__cin'), sectors = F('account_no__sectors'), account_type = F('account_no__account_type'))

    #
    # TAB- LGD
    #==============================================================
    if tab_status == "lgd":

        product_qry = """select product_name from app_basel_product_master where id = (select distinct(product_id) from app_collateral where account_no_id = app_lgd_final.account_no_id)"""

        results = constants.TAB_ACTIVE[tab_status][4].extra(select={'product_name': product_qry}).select_related("account_no")

        if acc_no_ins is not None:
            results = results.filter(account_no__in = acc_no_ins)

        if start_date is not None:
            if start_date !="":
                results = results.filter(date__gte = start_date)

        if end_date is not None:
            if end_date !="":
                results = results.filter(date__lte = end_date)

        results = results.values('id', 'date', 'account_no_id', 'ead_os', 'pv_cashflows', 'pv_cost', 'beta_value', 'sec_flag', 'factor_4', 'factor_5', 'avg_1', 'avg_2', 'avg_3', 'avg_4', 'avg_5', 'mgmt_overlay_1', 'mgmt_overlay_2', Account_No = F('account_no__account_no'), cin = F('account_no__cin'), sectors = F('account_no__sectors'), account_type = F('account_no__account_type')).order_by("id")

    #
    # TAB- Stage
    #==============================================================
    if tab_status == "stage":

        product_qry = """select product_name from app_basel_product_master where id = (select distinct(product_id) from app_collateral where account_no_id = app_stage_final.account_no_id)"""

        results = constants.TAB_ACTIVE[tab_status][4].extra(select={'product_name': product_qry}).select_related("account_no")

        if acc_no_ins is not None:
            results = results.filter(account_no__in = acc_no_ins)

        if start_date is not None:
            if start_date !="":
                results = results.filter(date__gte = start_date)

        if end_date is not None:
            if end_date !="":
                results = results.filter(date__lte = end_date)

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

        where = False

        if acc_no_ins is not None:
            if not where:
                qry += " where "
                where = True

            acc_qry = ','.join([str(x.id) for x in acc_no_ins])
            qry += " ED.account_no_id in ({0})".format(acc_qry)

        if start_date is not None:
            if start_date !="":
                if not where:
                    qry += " where "
                    where = True
                else:
                    qry += " and "

                qry += " ED.date >= {0}".format(start_date)


        if end_date is not None:
            if end_date !="":
                if not where:
                    qry += " where "
                    where = True
                else:
                    qry += " and "

                qry += " ED.date <= {0}".format(end_date)

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
    # TAB- EIR
    #==============================================================
    if tab_status == "eir":

        product_qry = """select product_name from app_basel_product_master where id = (select distinct(product_id) from app_collateral where account_no_id = app_eir_final.account_no_id)"""

        results = constants.TAB_ACTIVE[tab_status][4].extra(select={'product_name': product_qry}).select_related("account_no")

        if acc_no_ins is not None:
            results = results.filter(account_no__in = acc_no_ins)

        if start_date is not None:
            if start_date !="":
                results = results.filter(date__gte = start_date)

        if end_date is not None:
            if end_date !="":
                results = results.filter(date__lte = end_date)

        results = results.values('id', 'date', 'account_no_id', 'product_name', 'period', 'loan_availed', 'cost_avail', 'rate', 'emi', 'os_principal', 'os_interest', 'fair_value', 'coupon', 'discount_factor', 'col_1', 'col_2', 'col_3', 'default_eir', 'cop_tagged', Account_No = F('account_no__account_no'), cin = F('account_no__cin'), sectors = F('account_no__sectors'), account_type = F('account_no__account_type')).order_by("id")
        
    #
    # TAB- ECL
    #==============================================================
    if tab_status == "ecl":

        product_qry = """select product_name from app_basel_product_master where id = (select distinct(product_id) from app_collateral where account_no_id = app_ecl_final.account_no_id)"""

        results = constants.TAB_ACTIVE[tab_status][4].extra(select={'product_name': product_qry}).select_related("account_no")

        if acc_no_ins is not None:
            results = results.filter(account_no__in = acc_no_ins)

        if start_date is not None:
            if start_date !="":
                results = results.filter(date__gte = start_date)

        if end_date is not None:
            if end_date !="":
                results = results.filter(date__lte = end_date)


        results = results.values('id', 'date', 'account_no_id', 'product_name', 'tenure', Account_No = F('account_no__account_no'), cin = F('account_no__cin'), sectors = F('account_no__sectors'), account_type = F('account_no__account_type')).order_by("id")


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
    data["js_files"] = ['custom_js/imports.js?version=1.1.2']
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


    #==================================================================================
    # check if one is selected or with a single default
    #==================================================================================

    do_process = True

    if s_type == 1:
        results = constants.TAB_ACTIVE["pd"][3].filter(account_no__isnull = False)
    else:
        results = constants.TAB_ACTIVE["pd"][4]

    if id_selected is None or len(id_selected) == 0:

        if start_date is None and end_date is None and account_no is None:
            results = results.all()

        if start_date is not None:
            if end_date is not None:
                results = results.filter(date__gte = start_date, date__lte = end_date)
            else:
                results = results.filter(date__gte = start_date)

        if account_no is not None:
            results = results.filter(account_no__account_no__in = account_no)
    else:
        results = results.filter(id__in = id_selected)

    results = results.values('default_col')

    defaults = set([row["default_col"] for row in results])


    if len(defaults) <= 1:
        messages.error(request, "Operation not permitted. Try with multiple rows selected with different default values.")

        if account_no is None and start_date is not None and end_date is not None and id_selected is not None:
            rev = reverse("show_reports")
            params = request.POST.urlencode()
            rev = '{}{}?{}'.format(rev, "pd", params)
            return redirect(rev)
        else:
            return redirect("show_reports", "pd")

    #
    #
    #=============================================================================

    if do_process:
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
            rev = '{}{}?{}'.format(rev, "pd", params)
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
            rev = '{}{}?{}'.format(rev, "lgd", params)
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
            rev = '{}{}?{}'.format(rev, "stage", params)
            return redirect(rev)
        else:
            return redirect("show_reports", "stage")



#**********************************************************************
# ENDPOINT: GENERATE REPORT - STAGE
#**********************************************************************
def ead_report(request, s_type=0):

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

    ret = background_tasks.ead_report(request, start_date = start_date, end_date = end_date, account_no = account_no, s_type = s_type, id_selected = id_selected)
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
            rev = reverse("show_reports", "ead")
            params = request.POST.urlencode()
            rev = '{}{}?{}'.format(rev, "ead", params)
            return redirect(rev)
        else:
            return redirect("show_reports", "ead")



#**********************************************************************
# ENDPOINT: GENERATE REPORT - EIR
#**********************************************************************
def eir_report(request, s_type=0):

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

    results = None
    ret = background_tasks.eir_report(request, start_date = start_date, end_date = end_date, account_no = account_no, s_type = s_type, id_selected = id_selected)
    if ret:
        pass



    if request.is_ajax():
        if ret:
            return JsonResponse({"ret":ret, "msg":"EIR Report Created Successfully", "results":list(results)})
        else:
            return JsonResponse({"ret":ret, "msg":"EIR Report Creation Failed"})
    else:
        messages.success(request, "Report Generated Successfully")

        if account_no is None and start_date is not None and end_date is not None and id_selected is not None:
            rev = reverse("show_reports")
            params = request.POST.urlencode()
            rev = '{}{}?{}'.format(rev, "eir", params)
            return redirect(rev)
        else:
            return redirect("show_reports", "eir")


#**********************************************************************
# ENDPOINT: GENERATE REPORT - ECL
#**********************************************************************
def ecl_report(request, s_type=0):

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
    ret = background_tasks.ecl_report(request, start_date = start_date, end_date = end_date, account_no = account_no, s_type = s_type, id_selected = id_selected)
    if ret:

        qry = """
            select BP.product_name, BP.product_code, AC.account_no as Account_no, AC.cin, AC.sectors, AC.account_type, ECL.id as id, ECL.tenure, PD.pd, LGD.final_lgd, ST.stage, EAD.ead_total
            from app_ecl_reports ECL
            left join app_collateral C1 on C1.account_no_id = ECL.account_no_id
    		left join app_accountmaster AC on ECL.account_no_id = AC.id
            left join app_basel_product_master BP on C1.product_id = BP.id
            left join app_pd_report PD on PD.account_no_id = ECL.account_no_id and PD.date = ECL.date
            left join app_lgd_report LGD on LGD.account_no_id = ECL.account_no_id and LGD.date = ECL.date
            left join app_stage_report ST on ST.account_no_id = ECL.account_no_id and ST.date = ECL.date
            left join app_ead_report EAD on EAD.account_no_id = ECL.account_no_id and EAD.date = ECL.date
        """

        results = constants.TAB_ACTIVE["ecl"][4].raw(qry)

    if request.is_ajax():
        if ret:
            return JsonResponse({"ret":ret, "msg":"ECL Report Created Successfully", "results":list(results)})
        else:
            return JsonResponse({"ret":ret, "msg":"ECL Report Creation Failed"})
    else:
        messages.success(request, "Report Generated Successfully")

        if account_no is None and start_date is not None and end_date is not None and id_selected is not None:
            rev = reverse("show_reports")
            params = request.POST.urlencode()
            rev = '{}{}?{}'.format(rev, "ecl", params)
            return redirect(rev)
        else:
            return redirect("show_reports", "ecl")



#**********************************************************************
# ENDPOINT: REPORT - SHOW
#**********************************************************************
def show_reports(request, tab_status=None):

    data = defaultdict()

    account_no = None
    start_date = None
    end_date = None

    results = []

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
            acc_ids = None

            for i in account_no:
                acc = [str(x[0]) for x in AccountMaster.objects.filter(account_no__icontains = i).values_list("id")]
                acc_ids = ''.join(acc)

            if where_clause and acc_ids is not None:
                acc_cond = " and ED.account_no_id in ({})".format(acc_ids)
            else:
                if acc_ids is not None:
                    acc_cond = " where ED.account_no_id in ({})".format(acc_ids)

        #
        #
        data["counter"] = [1]
        counters = constants.TAB_ACTIVE[tab_status][4].raw("""select max(ads.id) as id from (select count(*) as id from app_collateral group by account_no_id) ads""")

        for x in counters:
            data["counter"] = range(1, int(x.id)+1)

        qry = """
            select ED.date, ED.id, ED.outstanding_amount, ED.undrawn_upto_1_yr, ED.undrawn_greater_than_1_yr, AC.account_no as Account_no, AC.account_type, AC.sectors, AC.cin, C.collateral_value, C.collateral_rating as c_rating, C.collateral_residual_maturity as c_r_maturity, BP.product_name, BP.product_code, BC.collateral_code, BC.collateral_type, BC.issuer_type, BC.collateral_eligibity, BC.rating_available, BC.collateral_rating as b_c_rating, BC.residual_maturity, BC.basel_collateral_type, BC.basel_collateral_subtype, BC.basel_collateral_code, BC.basel_collateral_rating, BC.soverign_issuer, BC.other_issuer, ED.ead_total, BC.residual_maturity as b_c_maturity
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
                "b_c_maturity":row.b_c_maturity,
                "basel_collateral_type":row.basel_collateral_type,
                "basel_collateral_subtype":row.basel_collateral_subtype,
                "basel_collateral_code":row.basel_collateral_code,
                "basel_collateral_rating":row.basel_collateral_rating,
                "soverign_issuer":row.soverign_issuer,
                "other_issuer":row.other_issuer,
                "bg_color":helpers.bg_color_codes(),
            })

    #
    #
    #=============================================================

    if tab_status == "ecl":

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
                    dates_cond = " where ECL.date >='{}' and ECL.date <='{}'".format(start_date, end_date)
                    where_clause = True
                else:
                    dates_cond = " where ECL.date >='{}'".format(start_date)
                    where_clause = True

        if account_no is not None:
            acc_ids = None

            for i in account_no:
                acc = [str(x[0]) for x in AccountMaster.objects.filter(account_no__icontains = i).values_list("id")]
                acc_ids = ''.join(acc)

            if where_clause and acc_ids is not None:
                acc_cond = " and ECL.account_no_id in ({})".format(acc_ids)
            else:
                if acc_ids is not None:
                    acc_cond = " where ECL.account_no_id in ({})".format(acc_ids)


        qry = """
            select BP.product_name, BP.product_code, AC.account_no as Account_no, AC.cin, AC.sectors, AC.account_type, ECL.date, ECL.id as id, ECL.tenure, PD.pd, LGD.final_lgd, ST.stage, EAD.ead_total, ECL.final_ecl, ECL.eir
            from app_ecl_reports ECL
            left join (select * from app_collateral group by account_no_id) C1 on ECL.account_no_id = C1.account_no_id
    		left join app_accountmaster AC on ECL.account_no_id = AC.id
            left join app_basel_product_master BP on C1.product_id = BP.id
            left join app_pd_report PD on PD.account_no_id = ECL.account_no_id and PD.date = ECL.date
            left join app_lgd_report LGD on LGD.account_no_id = ECL.account_no_id and LGD.date = ECL.date
            left join app_stage_report ST on ST.account_no_id = ECL.account_no_id and ST.date = ECL.date
            left join app_ead_report EAD on EAD.account_no_id = ECL.account_no_id and EAD.date = ECL.date {} {} and ECL.account_no_id is not null order by ECL.id
        """.format(dates_cond, acc_cond)

        results = constants.TAB_ACTIVE[tab_status][4].raw(qry)

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
    data["js_files"] = ['custom_js/imports.js?version=1.2.2']
    data["sidebar_active"] = 7
    data["items_list"] = results

    return render(request, "administrator/index.html", data)


#**********************************************************************
# ENDPOINT: UPLOAD COLLATERAl
#**********************************************************************

def collateral_upload(request):
    csv_file = request.FILES['formFile']
    insert_type = request.POST.get('insert_type')
    
    

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
        
        col_val = []
        for x in collateral_cols:
            
            #
            #
            if row[x].strip() != "":
                
                collateral_values = row[x].strip().split("|")
                
                collateral_ins = None

                try:
                    collateral_ins = Basel_Collateral_Master.objects.get(basel_collateral_code = collateral_values[0])
                except ObjectDoesNotExist:
                    if row[x].strip() != "":
                        err_msg["collateral_code"].append(row[x])
                        
                col_val.append(collateral_ins)
                
                # Run only if accoun_ins, product_ins and collateral_ins is not None
                # =================================================================
                if all([account_ins, product_ins, collateral_ins]):
                    
                    obj =  None
                    
                    #
                    # Insert depending on insert_type : 0 - Insert, 1 - Update

                    if int(insert_type) == 0:
                        obj = Collateral.objects.create(
                            account_no = account_ins,
                            product = product_ins,
                            collateral_code = collateral_ins
                        )
                    
                    elif int(insert_type) == 1:
                        try:
                            obj = Collateral.objects.get( account_no = account_ins, product = product_ins, collateral_code = collateral_ins)
                            
                        except MultipleObjectsReturned:
                            Collateral.objects.filter(account_no = account_ins, product = product_ins, collateral_code = collateral_ins).delete()
                            obj = Collateral.objects.create(
                                account_no = account_ins,
                                product = product_ins,
                                collateral_code = collateral_ins
                            )
                            
                        except ObjectDoesNotExist:
                            pass
                        
                    # 
                    #  Skip if obj is None

                    if obj is not None:
                        try:
                            obj.collateral_value = collateral_values[1] if collateral_values[1].strip() !="" else None
                        except IndexError:
                            pass

                        try:
                            obj.collateral_rating = collateral_values[2] if collateral_values[2].strip() !="" else None
                        except IndexError:
                            pass
                        
                        try:
                            obj.collateral_residual_maturity = collateral_values[3] if collateral_values[3].strip() !="" else None
                        except IndexError:
                            pass
                        
                        obj.save()

        #
        # =================================================================
        only_product = list(filter(None, col_val))

        if len(only_product) == 0:
            if account_ins is not None and product_ins is not None:
                
                #
                # Insert depending on insert_type : 1 - Insert, 2 - Update

                if int(insert_type) == 0:
                    try:
                        obj = Collateral.objects.create(
                            account_no = account_ins,
                            product = product_ins
                        )
                    except:
                        pass
                    
                else:
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
# METHOD TO DELETE DATA INTO RELEVANT FINAL MODELS
#**********************************************************************
def delete_final_single_record(request, tab_status=None, ins=None):
    try:
        constants.TAB_ACTIVE[tab_status][4].get(pk = int(ins)).delete()
        messages.success(request, "Record Deleted Successfully")
    except:
        messages.error(request, "Operation Failed")

    return redirect("show_final_records", tab_status)


#**********************************************************************
# ENDPOINT: DELETE FROM FINAL TABLE
#**********************************************************************

def delete_final_records(request, tab_status):
    ins_list = request.POST.getlist("checkbox_one", None)

    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    if start_date is not None and end_date is not None:
        objs = constants.TAB_ACTIVE[tab_status][4].filter(date__gte = start_date, date__lte = end_date)

        if objs.count() > 0:
            objs.delete()
            messages.success(request, "Records Deleted Successfully")
        else:
            messages.error(request, "No Records to delete")
    else:
        if len(ins_list) == 0:
            objs = constants.TAB_ACTIVE[tab_status][4].all()

            if objs.count() > 0:
                objs.delete()
                messages.success(request, "Records Deleted Successfully")
            else:
                messages.error(request, "No Records to delete")
        else:
            objs = constants.TAB_ACTIVE[tab_status][4].filter(pk__in = ins_list)

            if objs.count() > 0:
                objs.delete()
                messages.success(request, "Records Deleted Successfully")
            else:
                messages.error(request, "No Records to delete")
    return HttpResponse("1")


#**********************************************************************
# METHOD TO DELETE DATA INTO RELEVANT REPORTS MODELS
#**********************************************************************

def delete_report_single_record(request, tab_status=None, ins=None):
    try:
        constants.TAB_ACTIVE[tab_status][9].get(pk = int(ins)).delete()
        messages.success(request, "Record Deleted Successfully")
    except:
        messages.error(request, "Operation Failed")

    return redirect("show_reports", tab_status)


#**********************************************************************
# ENDPOINT: DELETE FROM REPORTS TABLE
#**********************************************************************

def delete_report_records(request, tab_status):
    ins_list = request.POST.getlist("checkbox_one", None)

    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    if start_date is not None and end_date is not None:
        objs = constants.TAB_ACTIVE[tab_status][9].filter(date__gte = start_date, date__lte = end_date)

        if objs.count() > 0:
            objs.delete()
            messages.success(request, "Records Deleted Successfully")
        else:
            messages.error(request, "No Records to delete")
    else:
        if len(ins_list) == 0:
            objs = constants.TAB_ACTIVE[tab_status][9].all()

            if objs.count() > 0:
                objs.delete()
                messages.success(request, "Records Deleted Successfully")
            else:
                messages.error(request, "No Records to delete")
        else:
            objs = constants.TAB_ACTIVE[tab_status][9].filter(pk__in = ins_list)

            if objs.count() > 0:
                objs.delete()
                messages.success(request, "Records Deleted Successfully")
            else:
                messages.error(request, "No Records to delete")
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

    results = Collateral.objects.all().select_related('account_no', 'collateral_code', 'product').values('id', 'collateral_value', 'collateral_rating', 'collateral_residual_maturity', Account_no = F('account_no__account_no'), product_name = F('product__product_name'), product_code = F('product__product_code'), basel_collateral_code = F('collateral_code__basel_collateral_code'))

    items_list = defaultdict()
    jsdata = defaultdict()

    for row in results:
        items_list[row["Account_no"]] = {"data":[], "bgcolor" : helpers.bg_color_codes()}
        jsdata[row["id"]] = []

    for row in results:
        items_list[row["Account_no"]]["data"].append(row)
        jsdata[row["id"]].append(row)

    #
    # DATA
    #==============================================================
    data["tab_status"] = None
    data["tab_active"] = 1
    data["content_template"] = 'administrator/show_collaterals.html'
    data["js_files"] = ['']
    data["sidebar_active"] = 3
    data["items_list"] = items_list
    data["jsdata"] = json.dumps(jsdata)


    ratings = Basel_Collateral_Master.objects.all().values('id', 'collateral_rating', 'residual_maturity')

    data["collateral_rating_list"] = set([ x["collateral_rating"] for x in ratings if x["collateral_rating"] is not None ])
    data["collateral_maturity_list"] = set([ x["residual_maturity"] for x in ratings if x["residual_maturity"] is not None ])


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

    audit_list = Audit_Trail.objects.all().select_related("user").order_by("-id")

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

                if jdata["selected_ids"] is not None:
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

            if jdata["selected_ids"] is not None:
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


#**********************************************************************
# ENDPOINT: SHOW MISSING ECL
#**********************************************************************

def show_missing_ecl(request):

    data = defaultdict()

    qry = """
    select EM.*,
    PD.date as pd_date, A_PD.account_no as pd_account, PD.pd as pd_details,
    LGD.date as lgd_date, A_LGD.account_no as lgd_account, LGD.final_lgd as lgd_details,
    ST.date as st_date, A_ST.account_no as st_account, ST.stage as st_details,
    EAD.date as ead_date, A_EAD.account_no as ead_account, EAD.ead_total as ead_details,
    BP.product_name, BP.product_code, AC.account_no as Account_no, AC.cin, AC.sectors, AC.account_type
    from app_ecl_missing_reports EM
    left join (select * from app_collateral group by account_no_id) C1 on EM.account_no_id = C1.account_no_id
	left join app_basel_product_master BP on C1.product_id = BP.id
    left join app_accountmaster AC on EM.account_no_id = AC.id
	left join app_pd_report PD on ((PD.account_no_id = EM.account_no_id and PD.date = EM.date) or PD.id = EM.pd)
    left join app_lgd_report LGD on ((LGD.account_no_id = EM.account_no_id and LGD.date = EM.date) or LGD.id = EM.lgd)
    left join app_stage_report ST on ((ST.account_no_id = EM.account_no_id and ST.date = EM.date) or ST.id = EM.pd)
    left join app_ead_report EAD on ((EAD.account_no_id = EM.account_no_id and EAD.date = EM.date) or EAD.id = EM.pd)
    left join app_accountmaster A_PD on A_PD.id = PD.account_no_id
    left join app_accountmaster A_LGD on A_LGD.id = LGD.account_no_id
    left join app_accountmaster A_ST on A_ST.id = ST.account_no_id
    left join app_accountmaster A_EAD on A_EAD.id = EAD.account_no_id
    """

    results = ECL_Missing_Reports.objects.raw(qry)

    data["items_list"] = defaultdict()
    data["content_template"] = "reports/show_missing_ecl_reports.html"
    data["js_files"] = []
    data["sidebar_active"] = 7

    data["items_list"] = results

    return render(request, "administrator/index.html", data)


#**********************************************************************
# ENDPOINT: DELETE MISSING ECL
#**********************************************************************

def delete_missing_ecl(request):
    ECL_Missing_Reports.objects.all().delete()
    return redirect("show_missing_ecl")


#**********************************************************************
# ENDPOINT: DELETE MISSING ECL
#**********************************************************************

def download_missing_ecl(request, ftype=0):
    qry = """
    select EM.*,
    PD.date as pd_date, A_PD.account_no as pd_account, PD.pd as pd_details,
    LGD.date as lgd_date, A_LGD.account_no as lgd_account, LGD.final_lgd as lgd_details,
    ST.date as st_date, A_ST.account_no as st_account, ST.stage as st_details,
    EAD.date as ead_date, A_EAD.account_no as ead_account, EAD.ead_total as ead_details,
    BP.product_name, BP.product_code, AC.account_no as Account_no, AC.cin, AC.sectors, AC.account_type
    from app_ecl_missing_reports EM
    left join (select * from app_collateral group by account_no_id) C1 on EM.account_no_id = C1.account_no_id
	left join app_basel_product_master BP on C1.product_id = BP.id
    left join app_accountmaster AC on EM.account_no_id = AC.id
	left join app_pd_report PD on ((PD.account_no_id = EM.account_no_id and PD.date = EM.date) or PD.id = EM.pd)
    left join app_lgd_report LGD on ((LGD.account_no_id = EM.account_no_id and LGD.date = EM.date) or LGD.id = EM.lgd)
    left join app_stage_report ST on ((ST.account_no_id = EM.account_no_id and ST.date = EM.date) or ST.id = EM.pd)
    left join app_ead_report EAD on ((EAD.account_no_id = EM.account_no_id and EAD.date = EM.date) or EAD.id = EM.pd)
    left join app_accountmaster A_PD on A_PD.id = PD.account_no_id
    left join app_accountmaster A_LGD on A_LGD.id = LGD.account_no_id
    left join app_accountmaster A_ST on A_ST.id = ST.account_no_id
    left join app_accountmaster A_EAD on A_EAD.id = EAD.account_no_id
    """

    results = ECL_Missing_Reports.objects.raw(qry)
    
    items_list = []

    for row in results:
        
        data_dict = {
            "id":row.id,
            "date":row.date,
            "Account_no":row.Account_no,
            "account_type":row.account_type,
            "cin":row.cin,
            "sectors":row.sectors,
            "product_name":row.product_name,
            "product_code":row.product_code,
            "tenure":row.tenure,
            "PD": "", 
            "LGD": "",
            "Stage":"",
            "EIR":row.eir,
            "EAD":"",
            "ECL":""
        }
        
        if row.pd is not None:
            if row.pd == "No Record":
                data_dict["PD"] = row.pd
            else:
                data_dict["PD"] = "{} - [{}]".format(row.pd_date,row.pd_account)
        else:
            data_dict["PD"] = row.pd_details
        
        if row.lgd is not None:
            if row.lgd == "No Record":
                data_dict["LGD"] = row.pd
            else:
                data_dict["LGD"] = "{} - [{}]".format(row.lgd_date,row.lgd_account)
        else:
            data_dict["LGD"] = row.lgd_details
        
        if row.stage is not None:
            if row.stage == "No Record":
                data_dict["Stage"] = row.stage
            else:
                data_dict["Stage"] = "{} - [{}]".format(row.st_date,row.st_account)
        else:
            data_dict["Stage"] = row.st_details
        
        if row.ead is not None:
            if row.ead == "No Record":
                data_dict["EAD"] = row.ead
            else:
                data_dict["EAD"] = "{} - [{}]".format(row.ead_date,row.ead_account)
        else:
            data_dict["EAD"] = row.ead_details
        
        items_list.append(data_dict)

    #
    #
    df = pd.DataFrame(items_list)

    if ftype == 0:
        file_name = os.path.join(settings.REPORTS_DIR, "output.xlsx")
        df.to_excel(file_name, sheet_name='Sheet_name_1', float_format='%.5f', index=False)
        if os.path.exists(file_name):
            with open(file_name, "rb") as report:
                data = report.read()
                response = HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename={}_Report.xlsx'.format("EIR_Missing_Report")
                return response
    elif ftype == 1:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format("EIR_Missing_Report")
        df.to_csv(path_or_buf=response, float_format='%.5f', index=False)
        return response
    else:
        return redirect("show_missing_ecl")
    
   