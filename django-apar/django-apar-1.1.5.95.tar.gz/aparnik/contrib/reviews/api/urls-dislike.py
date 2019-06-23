from django.conf.urls import url

from .views import DislikeReviewSetAPIView, DislikeListAPIView, LikeDetailAPIView

app_name = 'reviews'

urlpatterns = [
    url(r'^$', DislikeListAPIView.as_view(), name='list'),
    url(r'^set/$', DislikeReviewSetAPIView.as_view(), name='set'),
    url(r'^(?P<like_id>\d+)/$', LikeDetailAPIView.as_view(), name='detail'),
]