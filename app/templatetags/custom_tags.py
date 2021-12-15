#
# AUTHOR : LAWRENCE GANDHAR
# Project For Theo - (Greece)
# Project Date : 28th March 2021
#

import html

from django import template
from django.conf import settings
from django.utils import timezone, safestring
import html
from app.models import *
from app.helpers import *
from django.contrib.auth.models import User
import json

# use Library
register = template.Library()



# *********************************************************************************
#   Tag for loading css files
# *********************************************************************************

@register.simple_tag
def load_css_files(scripts = list()):

    html = []

    for script in scripts:
        html.append('<link rel="stylesheet" href="'+settings.STATIC_URL+script+'"/>')

    return safestring.mark_safe(''.join(html))


# *********************************************************************************
#   Tag for loading javascript files
# *********************************************************************************

@register.simple_tag
def load_javascript_files(scripts = list()):

    html = []

    for script in scripts:
        html.append('<script src="'+settings.STATIC_URL+script+'"></script>')

    return safestring.mark_safe(''.join(html))


# *********************************************************************************
#   PAGINATION HTML
# *********************************************************************************

@register.simple_tag
def pagination_html(page_obj, url = ""):

    dc = page_obj.paginator

    html = []
    html.append('<p class="text-center" style="background-color: #24262d; color: #ffffff; padding:7px 10px;border: 1px solid #3d404c;">')
    html.append('<strong>Page '+ str(page_obj.number)+ ' of '+ str(page_obj.paginator.num_pages)+'</strong>')
    html.append('</p>')
    html.append('<ul class="pagination pull-right" style="margin: 0px;">')

    for i in dc.page_range:
        html.append('<li>'+'<a href="'+url+'?page='+str(i)+'">'+str(i)+'</a></li>')

    html.append('</ul>')

    return safestring.mark_safe(''.join(html))


# *********************************************************************************
#   TICK MARK - ICON FOR TRUE AND FALSE
# *********************************************************************************

@register.simple_tag
def tick_mark(value):
    if value:
        html = '<span class="la la-check" style="color:#2db715; font-size: 25px;"></span>'
    else:
        html = '<span class="la la-times" style="color:#FF0000; font-size: 25px;"></span>'

    return safestring.mark_safe(html)


# *********************************************************************************
#   DATE TIME FORMATTER
# *********************************************************************************

@register.filter
def date_format(value):
    if value is not None:
        return value.strftime("%Y-%m-%d %H:%M")
    return ''


# *********************************************************************************
#   DATE TIME FORMATTER
# *********************************************************************************

@register.filter
def unescape_html(value):
    if value is not None:
        return html.unescape(value)
    return ''

# *********************************************************************************
#   MINUTES TO TIME FORMATTER
# *********************************************************************************

@register.simple_tag
def min_to_time(value):
    if value is not None and value > 0:

        if value < 60:
            return "{} mins".format(value)
        else:
            try:
                return "{} Hrs {} mins".format(*divmod(int(value), 60))
            except:
                pass
    return ''

# *********************************************************************************
# IF IN LIST
# *********************************************************************************

@register.filter
def if_in(value, args):
    if value is not None and args is not None:
        li = args.strip().split(',')

        if value in li:
            return True
        return False
    return False


# *********************************************************************************
# QUERYSET ROW TO JSON
# *********************************************************************************

@register.filter
def row_to_json(value):
    if value is not None:
        print(json.dumps(list(value)))
        return True
    return False


# *********************************************************************************
# QUERYSET ROW TO JSON
# *********************************************************************************
@register.filter
def replace(value, arg):
    """
    Replacing filter
    Use `{{ "aaa"|replace:"a|b" }}`
    """
    if len(arg.split('|')) != 2:
        return value

    what, to = arg.split('|')
    return value.replace(what, to)
