# -*- coding: utf-8 -*-
from congo.conf import settings
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.http.response import Http404, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.utils import translation
from django.utils.datastructures import OrderedDict
from django.utils.deprecation import MiddlewareMixin
from django.utils.encoding import force_text
import logging
import re

class SiteMiddleware(MiddlewareMixin):
    """Middleware który ustawia CONGO_SITE_MODEL na podstawie domeny"""

    def process_request(self, request):
        is_admin_backend = getattr(request, 'is_admin_backend', False)

        model_name = settings.CONGO_SITE_MODEL
        if not model_name:
            raise ImproperlyConfigured("In order to use Site model, configure settings.CONGO_SITE_MODEL first.")
        model = apps.get_model(*model_name.split('.', 1))

        try:
            site = model.objects.get_by_request(request)
            settings.SITE_ID = site.id
            request.site = site

            if not site.is_active and not is_admin_backend:
                raise Http404("Site not active for domain %s" % site.domain)

        except model.DoesNotExist:
            if settings.DEBUG:
                site = model.objects.get_by_id(settings.SITE_ID)
                request.site = site
            else:
                raise Http404("Site not found for domain %s" % request.get_host())

class SiteLanguageMiddleware(MiddlewareMixin):
    """Middleware który ustawia język na podstawie site'a"""

    def process_request(self, request):
        is_admin_backend = getattr(request, 'is_admin_backend', False)

        site = getattr(request, 'site')
        if site:
            if is_admin_backend:
                language = settings.CONGO_ADMIN_LANGUAGE_CODE
            else:
                language = site.language
            translation.activate(language)
            request.LANGUAGE_CODE = translation.get_language()

class UrlRedirectMiddleware(MiddlewareMixin):
    """Middleware realizujący przekierowania z CONGO_URL_REDIRECT_MODEL"""

    def process_response(self, request, response):
        model_name = settings.CONGO_URL_REDIRECT_MODEL
        if not model_name:
            raise ImproperlyConfigured("In order to use UrlRedirect model, configure settings.CONGO_URL_REDIRECT_MODEL first.")

        if response.status_code == 404:
            model = apps.get_model(*model_name.split('.', 1))
            redirect_url, is_permanent_redirect = model.get_redirect_tuple(request.get_full_path())
            if redirect_url:
                if is_permanent_redirect:
                    return HttpResponsePermanentRedirect(redirect_url)
                else:
                    return HttpResponseRedirect(redirect_url)

        return response

class BrokenLinkLogMiddleware(MiddlewareMixin):
    """Middleware logujący wszystkie błędne linki"""

    def process_response(self, request, response):
        if response.status_code == 404 and not settings.DEBUG:
            domain = request.get_host()
            path = request.get_full_path()
            referer = force_text(request.META.get('HTTP_REFERER', ''), errors = 'replace')

            if not self.is_ignorable_request(request, path, domain, referer):
                user_agent = request.META.get('HTTP_USER_AGENT', '<none>')
                remote_addr = request.META.get('REMOTE_ADDR', '<none>')

                extra = {
                    'user': request.user,
                    'extra_info': OrderedDict((
                        ('path', path),
                        ('domain', domain),
                        ('HTTP_REFERER', referer),
                        ('HTTP_USER_AGENT', user_agent),
                        ('REMOTE_ADDR', remote_addr),
                    )),
                }

                logger = logging.getLogger('django.http404')
                logger.warning(u"Not Found: %s", path, extra = extra)

        return response

    def is_internal_request(self, domain, referer):
        return bool(re.match("^https?://%s/" % re.escape(domain), referer))

    def is_ignorable_request(self, request, uri, domain, referer):
        if (not referer or (not self.is_internal_request(domain, referer) and '?' in referer)):
            return True
        return any(pattern.search(uri) for pattern in settings.IGNORABLE_404_URLS)
