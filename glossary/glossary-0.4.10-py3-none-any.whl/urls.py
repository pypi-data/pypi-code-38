from django.conf.urls import url

from .views import update

urlpatterns = [
    url(r'^update', update, name="glossary-update"),
]
