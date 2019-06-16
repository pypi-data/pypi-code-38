from django.conf.urls import url, include

app_name='aparnik'

urlpatterns = [
    url(r'^shops/', include('aparnik.packages.shops.urls.urls', namespace='shops')),
]
