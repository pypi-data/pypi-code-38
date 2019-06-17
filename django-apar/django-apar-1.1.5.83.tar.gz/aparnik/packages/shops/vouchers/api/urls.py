from django.conf.urls import url, include

from .views import VoucherListAPIView


app_name = 'vouchers'

urlpatterns = [
    url(r'^$', VoucherListAPIView.as_view(), name='list'),
    # url(r'^model/(?P<model_id>\d+)/set/$', BookmarkSetAPIView.as_view(), name='set'),

]