from django.conf.urls import url

from . import views

urlpatterns = [
    #url('^$', BaseView.as_view(), name='base'),
    url('^$', views.home, name='home'),

]
