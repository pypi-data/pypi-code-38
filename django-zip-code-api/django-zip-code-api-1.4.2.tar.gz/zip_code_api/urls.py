from django.conf.urls import url
from zip_code_api import views as zip_code_api_views

urlpatterns = [
#    url(r'^address-list/', zip_code_api_views.AddressList.as_view()),

    url(r'^zip-code/', zip_code_api_views.zip_code),
    url(r'^city/', zip_code_api_views.city),
    url(r'^street/', zip_code_api_views.street),
    url(r'^address/', zip_code_api_views.address),
]
