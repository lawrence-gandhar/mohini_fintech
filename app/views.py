#
# AUTHOR : LAWRENCE GANDHAR
# Project For Mohini - (India)
# Project Date : 14th Sep 2021
#

from django.views import View
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from collections import defaultdict
from . forms import NewUserForm
from django.contrib.auth.models import User
from django.conf import settings


#======================================================================
# Create Super user
#======================================================================

def create_superuser(request, ins=None):
    try:
        User.objects.create_superuser(username = settings.DJANGO_SUPERUSER_USERNAME,
                password = settings.DJANGO_SUPERUSER_PASSWORD,
                email = settings.DJANGO_SUPERUSER_EMAIL
        )
    except:
        pass
    
    data = defaultdict()
    data["username"] = settings.DJANGO_SUPERUSER_USERNAME
    data["password"] = settings.DJANGO_SUPERUSER_PASSWORD
    data["email"] = settings.DJANGO_SUPERUSER_EMAIL
    
    return render(request, "auth_templates/admin_details.html", data)


# ******************************************************************************
# LOGIN
# ******************************************************************************
class LoginView(View):
    template_name = 'auth_templates/login.html'

    data = defaultdict()

    data["css_files"] = []
    data["js_files"] = []

    def get(self, request):
        self.data["modal_open"] = False
        self.data["new_user_form"] = NewUserForm()

        return render(request, self.template_name, self.data)

    #
    def post(self, request):

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = authenticate(username=username, password=password)

        self.data["modal_open"] = True

        if user is not None:
            if user.is_active:
                login(request, user)

                if user.is_staff or user.is_superuser:
                    return redirect("admin_dashboard", permanent=True)
                else:
                    return redirect("user_dashboard", permanent=True)
            else:
                messages.error(request, 'Username is de-activated. Contact Administrator')
        else:
            messages.error(request, 'Invalid username or password')

        return render(request, self.template_name, self.data)


#
# ******************************************************************************
# PAGE 403
# ******************************************************************************
def page_403(request):
    return HttpResponse('')


#======================================================================
# Change Password
#======================================================================

def change_password(request):
    if request.POST:
        if validate_password(request.POST["password1"]):
            request.user.set_password(request.POST["password1"])
            update_session_auth_hash(request, request.user)
            request.user.save()
            return HttpResponse("Password Changed Successfully")
        return HttpResponse('This password must contain at least 8 characters.')
    return HttpResponse(0)


#======================================================================
# Validate Password
#======================================================================

def validate_password(password):
    if len(password) < 8:
        return False
    return True


#======================================================================
# Signup
#======================================================================

def signup(request):
    if request.POST:
        form = NewUserForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Mail will be sent to your email with all the details shortly.<br/></br/> Thank you for signing up..")
        else:
            messages.error(request, "Unable to process your request. Try again later.")
    return redirect("login")


#======================================================================
# Reset Password
#======================================================================

def reset_password(request, ins=None):
    if ins is not None:
        password = User.objects.make_random_password()

        try:
            user = User.objects.get(pk = int(ins))
            user.set_password(password)
            user.save()
            return HttpResponse(password)
        except:
            return HttpResponse(0)
    return HttpResponse(0)
