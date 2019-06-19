from django.conf.urls import url
from django.conf.urls import url, include
from dashboards_app.views import (
    DashboardDetail, DashboardList, AuthorDashboardList, CategoryDashboardList,
    YearDashboardList, MonthDashboardList, DayDashboardList, TagDashboardList,
    DashboardSearchResultsList,plugin_position)
from dashboards_app.feeds import LatestDashboardsFeed, TagFeed, CategoryFeed


from dashboards_app.plugins.form_addon_client.views import form_addon as form_addon_client
from dashboards_app.plugins.blero_grid_client.views import save_grid as save_grid_client


urlpatterns = [
    url(r'^$',
        DashboardList.as_view(), name='dashboard-list'),
    url(r'^feed/$', LatestDashboardsFeed(), name='dashboard-list-feed'),

    url(r'^search/$',
        DashboardSearchResultsList.as_view(), name='dashboard-search'),

    url(r'^(?P<year>\d{4})/$',
        YearDashboardList.as_view(), name='dashboard-list-by-year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        MonthDashboardList.as_view(), name='dashboard-list-by-month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$',
        DayDashboardList.as_view(), name='dashboard-list-by-day'),

    # Various permalink styles that we support
    # ----------------------------------------
    # This supports permalinks with <dashboard_pk>
    # NOTE: We cannot support /year/month/pk, /year/pk, or /pk, since these
    # patterns collide with the list/archive views, which we'd prefer to
    # continue to support.
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<pk>\d+)/$',
        DashboardDetail.as_view(), name='dashboard-detail'),
    # These support permalinks with <dashboard_slug>
    url(r'^(?P<slug>\w[-\w]*)/$',
        DashboardDetail.as_view(), name='dashboard-detail'),
    url(r'^(?P<year>\d{4})/(?P<slug>\w[-\w]*)/$',
        DashboardDetail.as_view(), name='dashboard-detail'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<slug>\w[-\w]*)/$',
        DashboardDetail.as_view(), name='dashboard-detail'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>\w[-\w]*)/$',  # flake8: NOQA
        DashboardDetail.as_view(), name='dashboard-detail'),

    url(r'^author/(?P<author>\w[-\w]*)/$',
        AuthorDashboardList.as_view(), name='dashboard-list-by-author'),

    url(r'^category/(?P<category>\w[-\w]*)/$',
        CategoryDashboardList.as_view(), name='dashboard-list-by-category'),
    url(r'^category/(?P<category>\w[-\w]*)/feed/$',
        CategoryFeed(), name='dashboard-list-by-category-feed'),

    url(r'^tag/(?P<tag>\w[-\w]*)/$',
        TagDashboardList.as_view(), name='dashboard-list-by-tag'),
    url(r'^tag/(?P<tag>\w[-\w]*)/feed/$',
        TagFeed(), name='dashboard-list-by-tag-feed'),

    url(r'^dash_doc/documentation/', include('dashboards_app.dash_docs_app.urls', namespace='dash_docs_app')),
    url(r'^plugins/plugin_position/(?P<plugin_type>[\w.-]+)/$', plugin_position,name='plugin_position'),
    url(r'^plugins/celery-progress/', include('dashboards_app.celery_progress.urls')),

    url(r'^plugins/form-addon-client/', form_addon_client),
    url(r'^plugins/blero_grid_client/', save_grid_client),
    url(r'^plugins/log_terminal_client/',
        include('dashboards_app.plugins.log_terminal_client.urls', namespace='log_terminal_client')),
    url(r'^plugins/task_tracker_client/', include('dashboards_app.plugins.task_tracker_client.urls', namespace='task_tracker_client')),



]
