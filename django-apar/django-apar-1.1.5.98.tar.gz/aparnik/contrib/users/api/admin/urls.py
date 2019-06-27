from django.conf.urls import url, include

from .views import UserSortAdminAPIView, UserAdminListAPIView

app_name = 'aparnik_users'

urlpatterns = [
    url(r'^$', UserAdminListAPIView.as_view(), name='list'),
    url(r'^sort/$', UserSortAdminAPIView.as_view(), name='sort'),
]
