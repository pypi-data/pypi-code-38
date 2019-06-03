""" Url router for the main application
"""
from django.conf.urls import url, include
from core_website_app.views.user import views as user_views

urlpatterns = [
    url(r'^account-request', user_views.request_new_account, name='core_website_app_account_request'),
    url(r'^contact', user_views.contact, name='core_website_app_contact'),
    url(r'^help', user_views.help_page, name='core_website_app_help'),
    url(r'^privacy', user_views.privacy_policy, name='core_website_app_privacy'),
    url(r'^terms', user_views.terms_of_use, name='core_website_app_terms'),

    url(r'^website/', include('core_website_app.rest.urls')),
]
