from django.conf.urls import url, include

from .views import NewsListAPIView

app_name = 'news'

urlpatterns = [
    url(r'^$', NewsListAPIView.as_view(), name='list'),
]
