#
# AUTHOR : LAWRENCE GANDHAR
# Project For Mohini - (India)
# Project Date : 14th Sept 2021
#

from django.contrib.auth.models import User
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.db import connection
from django.urls import reverse

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
# ENDPOINT: Database Management
#**********************************************************************
def database_management(request):
    data = defaultdict()
    data["content_template"] = "administrator/manage_process.html"
    data["js_files"] = []
    data["sidebar_active"] = 5

    return render(request, "administrator/index.html", data)


#**********************************************************************
# ENDPOINT: TRUNCATE ACCOUNTS TABLE
#**********************************************************************
def truncate_accounts_master(request):
    pass


#**********************************************************************
# ENDPOINT: TRUNCATE PD INITIAL TABLE
#**********************************************************************
def truncate_pd_initial(request):
    pass


#**********************************************************************
# ENDPOINT: TRUNCATE LGD INITIAL TABLE
#**********************************************************************
def truncate_lgd_initial(request):
    pass
