from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^(?P<dashboard_id>[0-9]+)/$', views.dashboard_doc_view, name='detail'),





    #plugins views




    ]
