from django.conf.urls import url, include

from .views import SubscriptionListAPIView

app_name = 'subscriptions'

urlpatterns = [
    url(r'^$', SubscriptionListAPIView.as_view(), name='list'),
]
