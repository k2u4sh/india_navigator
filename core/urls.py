# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include  # add this
from apps.api import urls as api_urls

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    path("", include("apps.authentication.urls")), # Auth routes - login / register

    # ADD NEW Routes HERE
    path('api-auth/', include('rest_framework.urls')),
    path('todos/', include(api_urls)),
    
    # Leave `Home.Urls` as last the last line
    path("", include("apps.home.urls")),

    
]
