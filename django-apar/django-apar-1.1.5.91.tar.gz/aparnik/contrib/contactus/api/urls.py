from django.conf.urls import url, include

from .views import ContactUsListAPIView, ContactUsDetailAPIView, ContactUsCreateAPIView

app_name = 'contactus'

urlpatterns = [
    url(r'^$', ContactUsListAPIView.as_view(), name='list'),
    url(r'^(?P<id>\d+)/$', ContactUsDetailAPIView.as_view(), name='details'),
    url(r'^create/$', ContactUsCreateAPIView.as_view(), name='create'),
]
