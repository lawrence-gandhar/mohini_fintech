#
# AUTHOR : LAWRENCE GANDHAR
# Project For Mohini - (India)
# Project Date : 14th Sept 2021
#


from . models import *
from django.contrib.auth.models import User
from django.forms import *
from django.contrib.auth.forms import UserCreationForm


# *************************************************************************************
# NEW USER FORM
# *************************************************************************************

class NewUserForm(ModelForm):
    class Meta:
        model = New_User

        fields = ('email', 'first_name', 'last_name',)

        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'email': TextInput(attrs={'class': 'form-control', 'type': 'email', 'required': 'true'}),
        }



# *************************************************************************************
# CREATE USER FORM
# *************************************************************************************

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'password1', 'password2')

        widgets = {
            'username': TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'first_name': TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'email': TextInput(attrs={'class': 'form-control', 'type': 'email', 'required': 'true'}),
            'is_superuser': CheckboxInput(attrs={'style': 'margin-left:10px;'}),
            'is_staff': CheckboxInput(attrs={'style': 'margin-left:10px;'}),
            'password1': TextInput(attrs={'class': 'form-control', 'type': 'password', 'required': 'true'}),
            'password2': TextInput(attrs={'class': 'form-control', 'type': 'password', 'required': 'true'}),
        }

# *************************************************************************************
# EDIT USER FORM
# *************************************************************************************


class EditUserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff')

        widgets = {
            'username': TextInput(attrs={'class':'form-control', 'required':'true', 'readonly':'true'}),
            'first_name': TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'required': 'true'}),
            'email': TextInput(attrs={'class': 'form-control', 'type': 'email', 'required': 'true'}),
            'is_superuser': CheckboxInput(attrs={'style': 'margin-left:10px;'}),
            'is_staff': CheckboxInput(attrs={'style': 'margin-left:10px;'}),
        }
