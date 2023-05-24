# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms

class UploadForm(forms.Form):
     file= forms.FileField() 