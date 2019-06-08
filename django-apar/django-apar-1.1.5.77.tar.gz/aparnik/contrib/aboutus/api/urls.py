from django.conf.urls import url, include

from .views import AboutusDetailAPIView

urlpatterns = [
    url(r'^$', AboutusDetailAPIView.as_view(), name='detail'),
]
