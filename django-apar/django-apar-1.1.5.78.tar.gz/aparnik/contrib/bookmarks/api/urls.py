from django.conf.urls import url, include

from .views import BookmarkListAPIView, BookmarkDetailAPIView, BookmarkSetAPIView

urlpatterns = [
    url(r'^$', BookmarkListAPIView.as_view(), name='list'),
    url(r'^model/(?P<model_id>\d+)/set/$', BookmarkSetAPIView.as_view(), name='set'),
    url(r'^(?P<bookmark_id>\d+)/$', BookmarkDetailAPIView.as_view(), name='detail'),
]