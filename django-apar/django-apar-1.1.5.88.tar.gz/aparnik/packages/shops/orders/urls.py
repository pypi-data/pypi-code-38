# -*- coding: utf-8 -*-


from django.conf.urls import url
from .views import invoice


# Create your views here.
app_name = 'orders'

urlpatterns = [
    url(r'^(?P<uuid>[0-9a-f-]+)/invoice/$', invoice, name='invoice'),
]
