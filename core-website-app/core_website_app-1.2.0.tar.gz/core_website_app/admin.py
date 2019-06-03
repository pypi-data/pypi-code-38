""" Url router for the administration site
"""
from django.conf.urls import url
from django.contrib import admin

import core_website_app.components.help.api as help_api
import core_website_app.components.privacy_policy.api as privacy_policy_api
import core_website_app.components.terms_of_use.api as terms_of_use_api
from core_main_app.components.web_page.models import WEB_PAGE_TYPES
from core_main_app.views.admin.views import WebPageView
from core_website_app.views.admin import views as admin_views, ajax as admin_ajax

admin_urls = [
    url(r'^user-requests$', admin_views.user_requests, name='core_website_app_user_requests'),
    url(r'^accept_request', admin_ajax.accept_request, name="core_website_app_accept_user_request"),
    url(r'^deny_request', admin_ajax.deny_request, name="core_website_app_deny_user_request"),
    url(r'^request_count', admin_ajax.account_request_count, name="core_website_app_request_count"),

    url(r'^contact-messages$', admin_views.contact_messages, name='core_website_app_contact_messages'),
    url(r'^remove_message', admin_ajax.remove_message, name="core_website_app_remove_contact_message"),
    url(r'^message_count', admin_ajax.contact_message_count, name="core_website_app_message_count"),

    url(r'^privacy-policy$',
        WebPageView.as_view(api=privacy_policy_api,
                            get_redirect='core_website_app/admin/privacy_policy.html',
                            post_redirect='admin:core_website_app_privacy',
                            web_page_type=WEB_PAGE_TYPES["privacy_policy"]),
        name='core_website_app_privacy'),

    url(r'^terms-of-use$',
        WebPageView.as_view(api=terms_of_use_api,
                            get_redirect='core_website_app/admin/terms_of_use.html',
                            post_redirect='admin:core_website_app_terms',
                            web_page_type=WEB_PAGE_TYPES["terms_of_use"]),
        name='core_website_app_terms'),

    url(r'^help$',
        WebPageView.as_view(api=help_api,
                            get_redirect='core_website_app/admin/help.html',
                            post_redirect='admin:core_website_app_help',
                            web_page_type=WEB_PAGE_TYPES["help"]),
        name='core_website_app_help'),
]

urls = admin.site.get_urls()
admin.site.get_urls = lambda: admin_urls + urls
