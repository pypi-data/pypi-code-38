
from django.urls import path

from django_orion_model.views import SubscriptionCallbackView

urlpatterns = [
    path('callback/{pk:pk}/', SubscriptionCallbackView.as_view(), name='orion_subscription_callback'),
]
