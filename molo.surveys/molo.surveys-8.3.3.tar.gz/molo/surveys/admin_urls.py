from django.conf.urls import url

from molo.surveys.views import index

urlpatterns = [
    # re-route to overwritten index view, originally in wagtailsurveys
    url(r'^$', index, name='index'),
]
