from django.conf.urls import url, include

urlpatterns = [
    url(r'^shops/', include('aparnik.packages.shops.urls.urls', namespace='shops')),
]
