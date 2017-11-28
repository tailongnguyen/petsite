# -*- coding: UTF-8 -*-
from django import forms
from .models import *
# from django import models

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ('phone', 'price', 'description', 'pet', 'image', 'available')

class EditPurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ('phone', 'price', 'description', 'image', 'available')


class EditProfileForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150)
    first_name = forms.CharField(label='First Name', max_length=30)
    last_name = forms.CharField(label='Last Name', max_length=30)
    email = forms.EmailField()
    gender = forms.CharField()
    dateOfBirth = forms.DateField()
    avatar = forms.ImageField()

class RegisterForm(forms.ModelForm):
    class Meta(object):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')
        
class SearchFrom(forms.Form):
    image = forms.ImageField()

class CommentForm(forms.ModelForm):
    class Meta(object):
        model = Comment
        fields = ('text',)