from django.conf.urls import url, include

from .views import NewsListAPIView

urlpatterns = [
    url(r'^$', NewsListAPIView.as_view(), name='list'),
]
