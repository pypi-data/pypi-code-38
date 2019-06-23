from django.conf.urls import url

from .views import LikeListAPIView, LikeDetailAPIView, LikeReviewSetAPIView

app_name = 'reviews'

urlpatterns = [
    url(r'^$', LikeListAPIView.as_view(), name='list'),
    url(r'^set/$', LikeReviewSetAPIView.as_view(), name='set'),
    url(r'^(?P<like_id>\d+)/$', LikeDetailAPIView.as_view(), name='detail'),
]