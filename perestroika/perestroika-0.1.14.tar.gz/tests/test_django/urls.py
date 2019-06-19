from django.urls import path

from tests.test_django.resources import EmptyResource, FullResource

urlpatterns = [
    path('empty/', EmptyResource().handler),
    path('full/', FullResource().handler),
]
