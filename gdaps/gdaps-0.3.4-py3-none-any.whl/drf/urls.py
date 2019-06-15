from django.urls import path, include
from django.views.generic import TemplateView

app_name = "gdaps"
# automatically include Django-REST-Framework's URLs
urlpatterns = []
# FIXME: rest_framework namespace can't chained?
# urlpatterns = [path("", include("rest_framework.urls"))]
