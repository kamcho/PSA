from  django import forms
from .models import MyUser
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
    class Meta:
        model=MyUser
        fields=['email','role']