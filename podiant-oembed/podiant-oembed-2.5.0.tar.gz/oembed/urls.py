from django.conf.urls import url
from .views import OEmbedProviderView, OEmbedAJAXView


urlpatterns = [
    url(r'^provider/$', OEmbedProviderView.as_view(), name='oembed_provider'),
    url(r'^object\.json$', OEmbedAJAXView.as_view(), name='oembed_object')
]
