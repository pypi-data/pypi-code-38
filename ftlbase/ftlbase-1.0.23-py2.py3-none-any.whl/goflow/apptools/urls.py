from django.conf.urls import url

from . import views

urlpatterns = [
    # url(r'^start/(?P<app_label>.*)/(?P<model_name>.*)/$', start_application),
    # url(r'^start_proto/(?P<process_name>.*)/$', start_application,
    #     {'form_class': forms.DefaultAppStartForm, 'template': 'goflow/start_proto.html'}),
    # url(r'^view_application/(?P<id>\d+)/$', view_application),
    url(r'^choice_application/(?P<id>\d+)/$', views.choice_application),
    # url(r'^process/(?P<id>\d+)/$', choice_application),
    url(r'^sendmail/$', views.sendmail),
    url(r'^application/testenv/(?P<action>create|remove)/(?P<id>.*)/$', views.app_env, name='app_env'),
    url(r'^application/teststart/(?P<id>.*)/$', views.test_start, name='test_start'),
]
