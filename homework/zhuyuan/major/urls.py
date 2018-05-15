# -*- coding: utf-8 -*-


from django.urls import path
from major.views import *

urlpatterns = [
    path('', download)
]