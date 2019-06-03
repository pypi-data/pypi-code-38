from django.conf.urls import url
from django.urls import path
#Import personales
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.select_app, name='select_app'),
    path('select_models/<str:app_name>', views.select_models, name='select_models'),
    path('dw/<str:app_name>', views.download, name='download'),
    path('up/<str:app_name>', views.restore, name='restore'),
 ]