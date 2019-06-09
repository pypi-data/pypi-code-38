from django.urls import path
from .views import OpenURL, Logs, Theme

urlpatterns = [

    path('open_url/', OpenURL.as_view(), name='radiant-open_url'),
    path('logs/', Logs.as_view(), name='radiant-logs'),
    path('mdc-theme.css/', Theme.as_view(), name='mdc-theme.css'),

]
