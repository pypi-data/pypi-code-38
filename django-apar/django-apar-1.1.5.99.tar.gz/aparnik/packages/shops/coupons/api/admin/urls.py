from django.conf.urls import url, include

from .views import CouponSortAdminAPIView, CouponAdminListAPIView

app_name = 'coupons'

urlpatterns = [
    url(r'^$', CouponAdminListAPIView.as_view(), name='list'),
    url(r'^sort/$', CouponSortAdminAPIView.as_view(), name='sort'),
]
