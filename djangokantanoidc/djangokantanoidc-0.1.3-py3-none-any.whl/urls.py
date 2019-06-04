# -*- coding: utf8 -*-
from django.urls import path
from .views import Callback, Start

app_name = 'kantanoidc'
urlpatterns = [
    path('start/', Start.as_view(), name='start'),
    path('callback/', Callback.as_view(), name='callback'),
]
