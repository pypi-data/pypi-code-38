from django.conf.urls import url, include

from .views import AboutusDetailAPIView

app_name = 'aboutus'

urlpatterns = [
    url(r'^$', AboutusDetailAPIView.as_view(), name='detail'),
]
