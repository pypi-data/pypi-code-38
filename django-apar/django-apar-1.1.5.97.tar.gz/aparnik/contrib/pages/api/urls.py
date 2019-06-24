from django.conf.urls import url, include

from .views import PageListAPIView

app_name = 'pages'

urlpatterns = [
    url(r'^$', PageListAPIView.as_view(), name='list'),
]
