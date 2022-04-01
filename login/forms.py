# coding=utf8
# Autor : Dennis zhang
# Time  : 2018/6/4 11:10
# File  : forms.py
# Software PyCharm

from django import forms

class UserForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=50)