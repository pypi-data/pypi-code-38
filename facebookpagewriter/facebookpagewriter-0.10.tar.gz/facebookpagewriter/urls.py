from django.conf.urls import url
from facebookpagewriter import views

urlpatterns = [
    url(r'', views.fblogin, name='fblogin'),
]
