from rest_framework import routers
from . import api_viewsets as views 
from django.conf.urls import re_path
from django.urls import include


urlpatterns = [
    re_path(r'^category/list/$', views.CategoryListViewset.as_view(), name='category_list_viewset'),
    re_path(r'^category/create/$', views.CategoryCreateViewset.as_view(), name='category_create_viewset'),
    re_path(r'^category/(?P<slug>[\w-]+)/$', views.CategoryRetrieveViewset.as_view(), name='category_retrieve_viewset'),
    re_path(r'^category/(?P<slug>[\w-]+)/update/$', views.CategoryUpdateViewset.as_view(), name='category_update_viewset'),
    re_path(r'^category/(?P<slug>[\w-]+)/destroy/$', views.CategoryDestroyViewset.as_view(), name='category_destroy_viewset'),            
]