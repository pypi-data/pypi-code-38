from django.conf.urls import url, include

from .views import QAListAPIView, QADetailAPIView, QACreateAPIView, QASortAPIView

app_name = 'questionanswers'

urlpatterns = [
    url(r'^$', QAListAPIView.as_view(), name='list'),
    url(r'^create/$', QACreateAPIView.as_view(), name='create'),
    url(r'^sort/$', QASortAPIView.as_view(), name='sort'),
    url(r'^model/(?P<model_id>\d+)/$', QAListAPIView.as_view(), name='models-list'),
    url(r'^(?P<qa_id>\d+)/$', QADetailAPIView.as_view(), name='detail'),
]