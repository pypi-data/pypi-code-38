""" Url router for the explore example application
"""
from django.conf.urls import url, include

from core_explore_example_app.utils.mongo_query import fields_to_query
from core_explore_example_app.views.user import views as user_views, ajax as user_ajax

urlpatterns = [
    url(r'^$', user_views.IndexView.as_view(),
        name='core_explore_example_index'),

    url(r'^rest/', include('core_explore_example_app.rest.urls')),

    url(r'^select-fields/(?P<template_id>\w+)$', user_views.SelectFieldsView.as_view(),
        name='core_explore_example_select_fields'),

    url(r'^build-query/(?P<template_id>\w+)$', user_views.BuildQueryView.as_view(),
        name='core_explore_example_build_query'),
    url(r'^build-query/(?P<template_id>\w+)/(?P<query_id>\w+)$', user_views.BuildQueryView.as_view(),
        name='core_explore_example_build_query'),
    url(r'^results/(?P<template_id>\w+)/(?P<query_id>\w+)$', user_views.ResultQueryView.as_view(),
        name='core_explore_example_results'),

    url(r'^save-fields$', user_ajax.save_fields,
        name='core_explore_example_save_fields'),
    url(r'^generate-element/(?P<explore_data_structure_id>\w+)$', user_ajax.generate_element,
        name='core_explore_example_generate_element'),
    url(r'^generate-choice/(?P<explore_data_structure_id>\w+)$', user_ajax.generate_choice,
        name='core_explore_example_generate_choice'),
    url(r'^remove-element$', user_ajax.remove_element,
        name='core_explore_example_remove_element'),

    url(r'^select-element$', user_ajax.select_element,
        name='core_explore_example_select_element'),
    url(r'^update-user-input$', user_ajax.update_user_input,
        name='core_explore_example_update_user_input'),

    url(r'^get-sub-elements-query-builder$', user_ajax.get_sub_elements_query_builder,
        name='core_explore_example_get_sub_elements_query_builder'),
    url(r'^insert-sub-elements-query$', user_ajax.insert_sub_elements_query,
        name='core_explore_example_insert_sub_elements_query'),

    url(r'^add-criteria$', user_ajax.add_criteria,
        name='core_explore_example_add_criteria'),
    url(r'^save-query$', user_ajax.SaveQueryView.as_view(
        fields_to_query_func=fields_to_query),
        name='core_explore_example_save_query'),
    url(r'^clear-criteria$', user_ajax.clear_criteria,
        name='core_explore_example_clear_criteria'),
    url(r'^clear-queries$', user_ajax.clear_queries,
        name='core_explore_example_clear_queries'),
    url(r'^delete-query$', user_ajax.delete_query,
        name='core_explore_example_delete_query'),
    url(r'^add-query-criteria$', user_ajax.add_query_criteria,
        name='core_explore_example_add_query_criteria'),
    url(r'^get-query$', user_ajax.GetQueryView.as_view(
        fields_to_query_func=fields_to_query),
        name='core_explore_example_get_query'),

    url(r'^get-persistent-query-url$', user_ajax.CreatePersistentQueryExampleUrlView.as_view(),
        name='core_explore_example_get_persistent_query_url'),
    url(r'^results-redirect/(?P<persistent_query_id>\w+)', user_views.ResultQueryExampleRedirectView.as_view(),
        name='core_explore_example_results_redirect'),
]
