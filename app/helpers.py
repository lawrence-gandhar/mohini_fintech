#
# AUTHOR : LAWRENCE GANDHAR
# Project For Mohini - (India)
# Project Date : 14th Sept 2021
#

import datetime
import os
import random
import string
import re
import json
from django.conf import settings
from app.models import *

from django.core.mail import EmailMessage
from django.core.serializers.json import DjangoJSONEncoder


# *************************************************************************************
# YEAR RANGE
# *************************************************************************************
def year_ranger():
    return [x for x in range(2011, (datetime.datetime.now().year + 5))]


# *************************************************************************************
# AUTO CODE GENERATOR
# *************************************************************************************

def generate_code(prefix="A", id=1):
    id = str(id)
    series = "0" * 10
    main_series = prefix + series[:(len(series) - len(id))] + id

    return main_series


# *************************************************************************************
# HANDLE UPLOADED FILE
# *************************************************************************************

def handle_uploaded_file(f, path="", insert_path=None):
    _, ext = os.path.splitext(f.name)

    file_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=14)) + ext

    filepath = os.path.join(path, file_name)

    with open(filepath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    if os.path.exists(filepath):
        if insert_path is not None:
            return [True, os.path.join(insert_path, file_name)]
        return [True, filepath]
    return [False, None]


# *************************************************************************************
# Create Directory
# *************************************************************************************

def create_directory(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            return True
        except:
            return False
    return True


# *************************************************************************************
# Remove Html Tags
# *************************************************************************************

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


# *************************************************************************************
# CHECK EXAM AND QUESTION VALIDITY
# *************************************************************************************

def check_exam_question(request, exam_id, ques_id):
    try:
        profile = Profile.objects.get(user=request.user)
        exam = Examinations.objects.get(pk=int(exam_id), is_active=True, class_name__in=(profile.class_name.all()),
                                        subject__in=(profile.subject.all()))
    except:
        return None, None

    try:
        question = Questions.objects.get(exam=exam, pk=int(ques_id), is_active=True)
        return exam, question
    except:
        None, None


# ******************************************************************************
# Send Email
# ******************************************************************************

def send_email_from_app(registered_exam):
    email_html_template = '''
        <html>
        <body>
        <p>
        Dear {} {},
        </br>
        </p>
        <p>
        </br>
            The evaluation for you last test is complete. Please login in the portal to check the results.
        </p>
        <p>
        <br/><br/>
        Thank you,<br/>
        Administrator<br/>
        Online Examination Portal<br/>
        </body></html>
    '''.format(registered_exam.student.first_name.title(), registered_exam.student.last_name.title())

    subject = '{} - Evaluation Status Updated'.format(registered_exam.exam.code)

    email_msg = EmailMessage(subject,
                             email_html_template,
                             settings.APPLICATION_EMAIL,
                             [registered_exam.student.email],
                             reply_to=[settings.APPLICATION_EMAIL]
                             )
    # this is the crucial part that sends email as html content but not as a plain text
    email_msg.content_subtype = 'html'
    email_msg.send(fail_silently=False)


# ******************************************************************************
# User Creation Form Errors Mapping
# ******************************************************************************
def user_creation_form_errors(err_msg):
    errors = json.loads(err_msg.as_json())
    err_keys = errors.keys()

    errors["password"] = []

    if "password2" in err_keys:
        for msg in errors["password2"]:
            errors["password"].append({"message":msg["message"], "code":msg["code"]})

        del(errors["password2"])

    if "password1" in err_keys:
        for msg in errors["password1"]:
            if msg["code"] == "required":
                errors["password"].append({"message":"Both password fields are required.", "code":msg["code"]})
            else:
                errors["password"].append({"message":msg["message"], "code":msg["code"]})

        del(errors["password1"])

    return errors


# ******************************************************************************
# Errors : Formatting
# ******************************************************************************
def format_errors(err_msg):

    if not isinstance(err_msg, dict) and isinstance(err_msg, str):
        err_msg = err_msg.as_json()

    html = ["<table style='color:#FFFFFF; border:1px solid #eee; width:100%'>"]
    html.append("<tr><td class='text-center' style='padding:10px; font-weight:700;'>Label</td>")
    html.append("<td class='text-center' style='padding:10px; font-weight:700;'>Errors</td></tr>")
    for i in err_msg:
        html.append("<tr><td style='vertical-align:top; padding:10px; border:1px solid #eee;'>{}</td>".format(i.title()))
        html.append("<td style='vertical-align:top; padding:10px; border:1px solid #eee;'><ul style='margin:0px;'>")
        for v in err_msg[i]:
            html.append("<li>{}</li>".format(v["message"]))
    html.append("</ul></td></tr></table>")

    html = ''.join(html)
    return html


# ******************************************************************************
# Queryset to {Row id:{row}} JSON format
# @queryset = Queryset Object
# ******************************************************************************
def queryset_row_to_json(queryset):
    items_list_json = {}
    for row in queryset:
        try:
            xx = row.__dict__  # get all attributes of the object
            items_list_json[row.id] = {x:y for (x,y) in xx.items() if x not in ["_state", "id"]}  # discard _state, id (key:value) pair
        except AttributeError:
            pass
            
        if "account_no_id" in items_list_json[row.id].keys():
            if items_list_json[row.id]["account_no_id"] is not None:
                acc_ins = AccountMaster.objects.get(pk = items_list_json[row.id]["account_no_id"])
                items_list_json[row.id]["account_no_id_related"] = acc_ins.account_no
            else:
                items_list_json[row.id]["account_no_id_related"] = None

    return json.dumps(items_list_json, cls=DjangoJSONEncoder)


# ******************************************************************************
#
# ******************************************************************************
def clean_data(val=None):
    if val is None:
        return None
    else:
        if val.strip()!="":
            return val.strip()
        else:
            return None
