from django.conf.urls import url, include

from .views import SubscriptionListAPIView

urlpatterns = [
    url(r'^$', SubscriptionListAPIView.as_view(), name='list'),
]
