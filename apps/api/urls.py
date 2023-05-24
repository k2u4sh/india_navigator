# todo/todo_api/urls.py : API urls.py
from django.conf.urls import url
from django.urls import path, include
from .views import getApiValue,getStates

urlpatterns = [
    path('getCal1', getApiValue),
    path('getStates', getStates),
  #
    
    
]