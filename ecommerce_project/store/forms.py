from django.contrib.auth.forms import UserCreationForm


from .models import User
from dataclasses import fields
from django.forms import ModelForm


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ["name", "avatar", "username", "email"]


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["name", "username", "email", "password", "password2"]
