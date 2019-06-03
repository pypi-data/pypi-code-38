""" Url router for the REST API
"""
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from core_explore_example_app.rest.saved_query import views as saved_query_views

urlpatterns = [
    url(r'^saved/query/$', saved_query_views.SavedQueryList.as_view(),
        name='core_explore_example_app_rest_saved_query_list'),

    url(r'^saved/query/(?P<pk>\w+)/$', saved_query_views.SavedQueryDetail.as_view(),
        name='core_explore_example_app_rest_saved_query_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
