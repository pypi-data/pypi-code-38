# -*- coding: utf-8 -*-

from django.urls import path, re_path

from . import views

app_name = "page"

urlpatterns = [
    re_path(r'^download/(?P<file_id>\d+)/', views.download, name='download'),

    path('post/<int:post_id>/', views.post, name='post'),
    path('post/<str:cate_id>/', views.post_list, name='post_list'),

    path('<int:page_id>/', views.page, name='page_by_id'),
    path('<slug:page_code>/', views.page, name='page_by_code'),

    path('', views.page, {'page_code': 'home'}, name='home'),
]
