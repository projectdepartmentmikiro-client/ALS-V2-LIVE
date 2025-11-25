# ALS/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["profile_image", "address"]
