from django.conf.urls import url, include

from .views import BookListAPIView, BookUserListAPIView

app_name = 'books'

urlpatterns = [
    url(r'^$', BookListAPIView.as_view(), name='list'),
    url(r'^user/$', BookUserListAPIView.as_view(), name='user'),
]
