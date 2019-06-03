
# -*- coding: utf-8 -*-
from rest_framework import routers


app_name = 'genomix_workflows'

# Simple router that can be extended in a main API
router = routers.SimpleRouter()

# Router with API Root
default_router = routers.DefaultRouter()

urlpatterns = default_router.urls
