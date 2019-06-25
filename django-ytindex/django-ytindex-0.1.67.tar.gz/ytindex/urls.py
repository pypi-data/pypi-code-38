from django.urls import path, re_path
from .views import search, count

urlpatterns = [
    re_path('(?P<index>\w*)/_count', count, name='ytindex-count'),
    re_path('(?P<index>\w*)/(?P<query>.*)', search, name='ytindex-search'),
]
