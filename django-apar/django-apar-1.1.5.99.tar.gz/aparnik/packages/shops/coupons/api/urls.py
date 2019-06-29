from django.conf.urls import url, include

app_name = 'coupons'

urlpatterns = [
    url(r'^admin/', include('aparnik.packages.shops.coupons.api.admin.urls', namespace='admin')),
]
