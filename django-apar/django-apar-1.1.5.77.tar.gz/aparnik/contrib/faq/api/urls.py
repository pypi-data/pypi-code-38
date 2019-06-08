from django.conf.urls import url, include

from .views import FAQDetailAPIView

urlpatterns = [
    url(r'^$', FAQDetailAPIView.as_view(), name='detail'),
]
