from .views import BlogContentView, BlogFileView
from django.urls import path
from django.urls.converters import PathConverter, register_converter


class EmptyPathConverter(PathConverter):
    regex = '.*'


register_converter(EmptyPathConverter, 'emptypath')

urlpatterns = [
    path('file/<path:url>', BlogFileView.as_view(), name='file'),
    path('<emptypath:url>', BlogContentView.as_view(), name='content'),
    path('', BlogContentView.as_view(), name='index'),
]
