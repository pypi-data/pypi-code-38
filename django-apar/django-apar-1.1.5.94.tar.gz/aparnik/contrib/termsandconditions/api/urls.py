from django.conf.urls import url, include

from .views import TermsAndConditionsDetailAPIView

app_name = 'termsandconditions'

urlpatterns = [
    url(r'^$', TermsAndConditionsDetailAPIView.as_view(), name='detail'),
]