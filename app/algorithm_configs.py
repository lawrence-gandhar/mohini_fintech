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
            
            obj = None
            
            if col_name not in ['date', 'account_no']:
                obj, created  = Pre_Defined_Variables.objects.update_or_create(
                    tab_status = x,
                    column_name = col_name,
                    show_in_reports = True,
                    show_in_download_reports = True,
                    column_name_in_reports = constants.REPORT_HEADERS[col_name]
                )
                
            if constants.TAB_ACTIVE[x][10] is not None and obj is not None:
                if col_name in constants.TAB_ACTIVE[x][10]:
                    obj.default_factor = True
                    obj.save()
        
    return HttpResponse(1) 
 
 
#**********************************************************************
# PREDEFINED VARIABES VIEW
#********************************************************************** 
class PredefinedVariarbles(View):
    
    data = defaultdict()
    data["content_template"] = "algo_config/predefined_variables.html"
    data["js_files"] = []
    data["sidebar_active"] = 8
    data["tab_status"] = "pd"
    data["report_headers"] = constants.REPORT_HEADERS
    
    def get(self, request, tab_status=None):
        self.data["pre_defined_variables"] = Pre_Defined_Variables.objects.filter(tab_status=tab_status)
        return render(request, "administrator/index.html", self.data)

    def post(self, request):
        pass
 
 
#**********************************************************************
# PREDEFINED VARIABES - DELETE
#********************************************************************** 
def change_status(request, ins=None, status=1):
    try:
        obj = Pre_Defined_Variables.objects.get(pk=int(ins))
        obj.is_active = bool(int(status))
        obj.save()
        
        if bool(int(status)):
            messages.success(request, "Variable Activated Successfully")
        else:
            messages.success(request, "Variable Deactivated Successfully") 
    except:
        messages.error(request, "Variable Status Change Failed")
    
    return redirect(request.META.get('HTTP_REFERER'))
 
 
#**********************************************************************
# PD - Configuring the algorithm
#**********************************************************************
class ConfigureTemplates(View):
    
    data = defaultdict()
    data["items_list"] = defaultdict()
    data["content_template"] = "algo_config/index.html"
    data["js_files"] = []
    data["sidebar_active"] = 8
    data["tab_status"] = "pd"
    data["algorithm"] = "LOGISTIC REGRESSION - Probability Of Default (PD)"
    data["report_headers"] = constants.REPORT_HEADERS
    data["template_id"] = 0
    
    #
    #
    def get(self, request, tab_status=None, template_id=0):
        
        self.data["tab_status"] = self.data["tab_status"] if tab_status is not None else self.data["tab_status"]
        
        self.data["pre_defined_variables"] = Pre_Defined_Variables.objects.filter(Q(tab_status__isnull=True) | Q(tab_status="master") | Q(tab_status=self.data["tab_status"])).filter(is_active=True)
        
        self.data["built_in_fields"] = self.data["pre_defined_variables"] 
        
        self.data["row_count"] = 0
        
        if template_id:
            algo_qry = Algo_Config.objects.filter(template_id=template_id).select_related("use_built_in_column")
            self.data["row_count"] = algo_qry.count()
            self.data["template_id"] = template_id
            self.data["algo_field_columns"] = algo_qry
        else:
            self.data["template_id"] = 0
            self.data["algo_field_columns"] = self.data["pre_defined_variables"]
          
        return render(request, "administrator/index.html", self.data)
        
    #
    #
    def post(self, request, tab_status=None):
       
        template_id = request.POST.get('template_id')
        template_name = request.POST.get('template_name') 
        is_active = request.POST.get('is_active') 
       
        tab_status = request.POST.get('tab_status') 
        column_name = request.POST.getlist('column_name')
        show_in_report = request.POST.getlist('show_in_report')
        show_in_download_reports = request.POST.getlist('show_in_download_reports')
        use_as_factor = request.POST.getlist('use_as_factor')
        use_built_in_column = request.POST.getlist('use_built_in_column')
        use_formula = request.POST.getlist('use_formula')
        
        
        if not bool(int(template_id)):
            if template_name.strip() == "":
                template_name = "Default"
                messages.error(request, "Blank Template name by default is set to 'Default'")
            else:
                temp_name_exists = ConfigTemplate.objects.filter(template=template_name.strip(), tab_status=tab_status).count()
                
                if temp_name_exists:
                    messages.error(request, "Template name already exists. Try a different one")
                    return redirect(request.META.get('HTTP_REFERER'))

        if template_name is not None:
            
            if template_name.strip() == "":
                template_name = "Default"
                messages.error(request, "Blank Template name by default is set to 'Default'")
            
            # Add Template
            #================================================================
            try:
                template_obj = ConfigTemplate.objects.get(pk=template_id)
                
                template_obj.template = template_name.strip()
                template_obj.set_as_default = True
                template_obj.algorithm = 1
                template_obj.is_active = bool(int(is_active))
                template_obj.save()
                
                Algo_Config.objects.filter(template=template_obj).delete()
                
            except ObjectDoesNotExist:
                template_obj = ConfigTemplate.objects.create(
                    template = template_name.strip(),
                    set_as_default = True,
                    algorithm = 1,
                    is_active = bool(int(is_active)),
                    user = request.user,
                    tab_status = tab_status,
                )
            
            
            # 
            #================================================================
            for i in range(len(column_name)):
                Algo_Config.objects.create(
                    tab_status=tab_status,
                    column_name = column_name[i],
                    show_in_reports = show_in_report[i],
                    show_in_download_reports = show_in_download_reports[i],
                    use_as_factor = use_as_factor[i],
                    use_built_in_column_id = use_built_in_column[i],
                    use_formula = use_formula[i],
                    template = template_obj
                )
            
            messages.success(request, "Template Added Successfully")
            return redirect("pd_module_testing")
        else:
            messages.error(request, "Template name is required")
        return redirect(request.META.get('HTTP_REFERER'))
        
        
#**********************************************************************
# Template - Set As Default
#**********************************************************************    
def template_set_as_default(request, tab_status=None, template_id=None):
    if template_id is not None and tab_status is not None:
        ConfigTemplate.objects.filter(tab_status=tab_status, user=request.user).update(set_as_default=False)

        try:
            obj = ConfigTemplate.objects.get(pk=int(template_id))
            obj.set_as_default = True
            obj.save()
            messages.success(request, "Template Set As Default successfully")
        except:
            messages.error(request, "Operation On Template failed")       
    else:
        messages.error(request, "Operation On Template failed")    
    return redirect(request.META.get('HTTP_REFERER'))

    
#**********************************************************************
# Delete Template
#**********************************************************************    
def delete_template(request, ins=None):
    if ins is not None:
        try:
            ConfigTemplate.objects.get(pk=int(ins)).delete()
            messages.success(request, "Template deleted successfully")
        except:
            messages.error(request, "Template delete failed")       
    else:
        messages.error(request, "Operation On Template failed")    
        
    return redirect("pd_module_testing")
    
    
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


#**********************************************************************
# PD Template & Module Testing
#**********************************************************************
def pd_module_testing(request, algo_type=None):
    data = defaultdict()
    data["items_list"] = defaultdict()
    data["content_template"] = "algo_config/pd_module_test.html"
    data["js_files"] = []
    data["sidebar_active"] = 8
    data["tab_status"] = "pd"
    
    data["alorithm_buttons"] = [x for x in range(len(constants.PD_SOLVERS_LIST))]
    data["templates_list"] = ConfigTemplate.objects.filter(tab_status=data["tab_status"], user = request.user)
    
    if algo_type is not None:
        ret = background_tasks.pd_report(request, start_date = None, end_date = None, account_no = None, s_type = None, id_selected = None, algo_type=algo_type)
        
        if ret:
            return redirect("show_reports", data["tab_status"])
    
    return render(request, "administrator/index.html", data)

