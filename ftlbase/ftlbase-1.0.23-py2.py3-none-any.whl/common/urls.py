# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import include, url

from . import form as common_forms
from . import views as common_views

# from . import form

urlpatterns = [
    # url(r'^base_url.js$', common_views.base_url_js, name='common-base-url-js'),

    url(r'^login/$', common_views.loginX, name='loginX'),
    url(r'^logout/$', common_views.logoutX, name='logoutX'),

    # Workflow
    url(r'^workflow/action/(?P<id>\d+)/$', common_views.common_workflow,
        {'goto': 'workflow_pending', 'dictionary': {'acao': common_forms.ACAO_WORKFLOW_TO_APPROVE, 'disableMe': True}},
        name="workflow_action"),
    # url(r'^workflow/ratify/(?P<id>\d+)/$', common_views.common_workflow,
    #     {'goto': 'workflow_pending',
    #      'dictionary': {'acao': common_forms.ACAO_WORKFLOW_RATIFY, 'disableMe': True}}, name="workflow_to_ratify"),
    url(r'^workflow/workflow_execute/(?P<id>\d+)/$', common_views.common_workflow_execute,
        {'goto': 'workflow_pending', 'dictionary': {'disableMe': True}},
        name="workflow_execute_std"),

    url(r'^workflow/flag/news$', common_views.common_workflow_flag_news, name='workflow_flag_news'),
    url(r'^workflow/flag/myworks', common_views.common_workflow_flag_myworks, name='workflow_flag_myworks'),

    url(r'^workflow/news/$', common_views.common_workflow_table_process, {'news': True, 'add': False},
        name='workflow_news'),
    url(r'^workflow/myworks/$', common_views.common_workflow_table_process, {'my_work': True, 'add': False},
        name='workflow_myworks'),
    url(r'^workflow/pending/$', common_views.common_workflow_table_process, {'pending': True, 'add': False},
        name='workflow_pending'),
    url(r'^workflow/all/$', common_views.common_workflow_table_process, {'add': False}, name='workflow_all'),

    url(r'^workflow/graph/(?P<pk>\d+)/$', common_views.common_workflow_graph, name='workflow_graph'),
    url(r'^workflow/process_graph/(?P<title>.+)/$', common_views.common_process_graph, name='workflow_process_graph'),
    url(r'^workflow/history/(?P<pk>\d+)/$', common_views.common_history_workitems_table,
        {'goto': 'workflow_pending', 'model': common_forms.ProcessWorkItemTable},
        name="workflow_history"),

    url(r'^table/', include('table.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
