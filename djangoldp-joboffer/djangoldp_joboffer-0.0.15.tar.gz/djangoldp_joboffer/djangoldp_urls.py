from django.conf.urls import url
from .views import JobOffersViewset, JobOffersCurrentViewset, \
                   JobOffersExpiredViewset

urlpatterns = [
    url(r'^job-offers/current/', JobOffersCurrentViewset.urls()),
    url(r'^job-offers/expired/', JobOffersExpiredViewset.urls()),
    # Dirty fix for bad id change to job-offers/self/
    url(r'^job-offers/', JobOffersViewset.urls()),
]
