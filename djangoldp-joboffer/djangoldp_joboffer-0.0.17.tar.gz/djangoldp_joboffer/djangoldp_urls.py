from django.conf.urls import url
from .views import JobOffersCurrentViewset, \
                   JobOffersExpiredViewset

urlpatterns = [
    url(r'^job-offers/current/', JobOffersCurrentViewset.urls(model_prefix="joboffer-current")),
    url(r'^job-offers/expired/', JobOffersExpiredViewset.urls(model_prefix="joboffer-expired")),
]
