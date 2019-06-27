from django.conf.urls import url, include

from .views import FAQDetailAPIView

app_name = 'faq'

urlpatterns = [
    url(r'^$', FAQDetailAPIView.as_view(), name='detail'),
]
