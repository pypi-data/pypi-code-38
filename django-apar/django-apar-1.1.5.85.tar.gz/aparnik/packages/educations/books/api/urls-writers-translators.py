from django.conf.urls import url, include

from .views import WriterTranslatorListAPIView, WriterTranslatorDetailAPIView

app_name = 'books'

urlpatterns = [
    url(r'^$', WriterTranslatorListAPIView.as_view(), name='list'),
    url(r'^(?P<writer_translator_id>\d+)/$', WriterTranslatorDetailAPIView.as_view(), name='details'),
]
