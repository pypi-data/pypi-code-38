from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'test/(?P<identifier>[a-zA-Z-_.]+)/',
            views.EmailTestView.as_view()),
    re_path(r'$', views.EmailsView.as_view()),
]
