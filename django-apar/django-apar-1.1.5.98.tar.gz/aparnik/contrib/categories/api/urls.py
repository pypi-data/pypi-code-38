from django.conf.urls import url, include

from .views import CategoryListAPIView, CategoryListModelAPIView#, CategoryCourseListAPIView, CategoryLibraryListAPIView

app_name = 'categories'

urlpatterns = [
    url(r'^$', CategoryListAPIView.as_view(), name='list'),
    url(r'^(?P<category_id>\d+)/models$', CategoryListModelAPIView.as_view(), name='list-model'),
    url(r'^(?P<category_id>\d+)/childs$', CategoryListAPIView.as_view(), name='list-childs'),
]