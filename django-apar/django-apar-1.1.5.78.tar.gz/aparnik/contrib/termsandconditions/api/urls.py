from django.conf.urls import url, include

from .views import TermsAndConditionsDetailAPIView

urlpatterns = [
    url(r'^$', TermsAndConditionsDetailAPIView.as_view(), name='detail'),
]