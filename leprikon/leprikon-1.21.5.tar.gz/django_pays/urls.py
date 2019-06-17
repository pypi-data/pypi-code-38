from django.conf.urls import url
from django.db import transaction

from .views import confirm

app_name = 'pays'

urlpatterns = [
    url(r'^(?P<slug>[^/]+)/', transaction.atomic(confirm), name='confirm'),
]
