from django.conf.urls import url, include

from .views import PageListAPIView

urlpatterns = [
    url(r'^$', PageListAPIView.as_view(), name='list'),
]
