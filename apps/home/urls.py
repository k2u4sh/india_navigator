# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from .views import upload_user

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
     path('forms.html', upload_user, name="form"),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

    

]
