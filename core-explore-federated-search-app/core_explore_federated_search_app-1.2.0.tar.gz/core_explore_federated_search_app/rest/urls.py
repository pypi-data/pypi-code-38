""" Url router for the REST API
"""
from django.conf.urls import url
from core_explore_federated_search_app.rest.query import views as query_views
from core_explore_federated_search_app.rest.result import views as result_views

urlpatterns = [
    url(r'^execute-query', query_views.QueryExecute.as_view(),
        name='core_explore_federated_search_app_rest_execute_query'),
    url(r'^result', result_views.ResultDetail.as_view(),
        name='core_explore_federated_search_app_rest_get_result_from_data_id'),
]
