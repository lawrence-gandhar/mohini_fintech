#
# AUTHOR : LAWRENCE GANDHAR
# Project For Mohini - (India)
# Project Date : 3rd Feb 2022
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
# LOAD PREDEFINED VARIABES
#**********************************************************************

def load_predefined_variables(request):
    
    # Date
    Pre_Defined_Variables.objects.update_or_create(
        tab_status = None,
        column_name = "date",
        show_in_reports = True,
        show_in_download_reports = True,
        column_name_in_reports = constants.REPORT_HEADERS["date"]
    )

    
    # Master & Product
    for x in ["master", "product"]:
        for col_name in constants.TAB_ACTIVE[x][2]:
            Pre_Defined_Variables.objects.update_or_create(
                tab_status = x,
                column_name = col_name,
                show_in_reports = True,
                show_in_download_reports = True,
                column_name_in_reports = constants.REPORT_HEADERS[col_name]
            )
    
    # Collateral
    for col_name in constants.TAB_ACTIVE["collateral"][2]:
        Pre_Defined_Variables.objects.update_or_create(
            tab_status = x,
            column_name = col_name,
            show_in_reports = False,
            show_in_download_reports = False,
            column_name_in_reports = constants.REPORT_HEADERS[col_name]
        )        
    
    # 
    for x in ['pd', 'lgd', 'ead', 'stage', 'ecl', 'eir']:
        for col_name in constants.TAB_ACTIVE[x][2]:
            if col_name not in ['date', 'account_no']:
                Pre_Defined_Variables.objects.update_or_create(
                    tab_status = x,
                    column_name = col_name,
                    show_in_reports = True,
                    show_in_download_reports = True,
                    column_name_in_reports = constants.REPORT_HEADERS[col_name]
                )
        
    return HttpResponse(1) 
 
 
#**********************************************************************
# PD - Configuring the algorithm
#**********************************************************************

class ConfigurePD(View):
    
    data = defaultdict()
    data["items_list"] = defaultdict()
    data["content_template"] = "algo_config/index.html"
    data["js_files"] = []
    data["sidebar_active"] = 8
    data["tab_status"] = "pd"
    data["algorithm"] = "LOGISTIC REGRESSION"
    data["sub_title"] = "Configure Import, Report & Algorithm Parameters for PD"
    data["reports_headers"] = constants.REPORT_HEADERS
    
    #
    #
    def get(self, request, tab_status=None):
        
        self.data["tab_status"] = self.data["tab_status"] if tab_status is not None else self.data["tab_status"]
        
        algo_qry = Algo_Config.objects.filter(tab_status=self.data["tab_status"])
        
        if algo_qry.count() > 0:
            self.data["algo_field_columns"] = [(x.id, x.column_name) for x in algo_qry]
        else:
            self.data["algo_field_columns"] = []    
            
        self.data["algo_fields"] = constants.TAB_ACTIVE[self.data["tab_status"]][10]
        self.data["pre_defined_variables"] = Pre_Defined_Variables.objects.all()
        self.data["algo_fields_qry"] = algo_qry
        
        return render(request, "administrator/index.html", self.data)
        
    #
    #
    def post(self, request):
       
        tab_status = request.POST.get('tab_status') 
        column_name = request.POST.getlist('column_name')
        show_in_report = request.POST.getlist('show_in_report')
        show_in_download_reports = request.POST.getlist('show_in_download_reports')
        use_as_factor = request.POST.getlist('use_as_factor')
        use_built_in_column = request.POST.getlist('use_built_in_column')
        use_formula = request.POST.getlist('use_formula')
        
        Algo_Config.objects.filter(tab_status = tab_status).delete()
        
        for i in range(len(column_name)):
            Algo_Config.objects.create(
                tab_status=tab_status,
                column_name = column_name[i],
                show_in_reports = show_in_report[i],
                show_in_download_reports = show_in_download_reports[i],
                use_as_factor = use_as_factor[i],
                use_built_in_column = use_built_in_column[i],
                use_formula = use_formula[i],
            )
        
        messages.success(request, "Parameters Added Successfully")
        return redirect(request.META.get('HTTP_REFERER'))
    
#**********************************************************************
# Delete Columns algorithm
#**********************************************************************

def delete_column_algoconfig(request, ins=None):
    try:
        Algo_Config.objects.get(pk = int(ins)).delete()
        messages.success(request, "Column deleted successfully")
    except:
        messages.error(request, "Column delete unsuccessfull")
    
    return redirect(request.META.get('HTTP_REFERER'))