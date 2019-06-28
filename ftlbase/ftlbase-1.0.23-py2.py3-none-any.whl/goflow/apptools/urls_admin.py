from django.conf.urls import url

from . import views

urlpatterns = [
    # (r'^icon/image_update/$', 'image_update'),
    url(r'^application/testenv/(?P<action>create|remove)/(?P<id>.*)/$', views.app_env.as_view(), name='app_env'),
    url(r'^application/teststart/(?P<id>.*)/$', views.test_start.as_view(), name='test_start'),
]
