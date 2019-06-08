from django.conf.urls import url

from . import views

# Add this pattern to project's urls if you want to enable downloads
# It must have "dbfile" namespace
# Example:
#   url(r'^download/', include(\"dbfile.urls\", namespace=\"dbfile\")

urlpatterns = [
    url(r'^(?P<filename>.+)$', views.download, name='download'),
]
