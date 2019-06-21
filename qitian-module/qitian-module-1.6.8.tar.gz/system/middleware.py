from django.utils.deprecation import MiddlewareMixin

from django.contrib.sites.models import Site
from django.http.request import split_domain_port

SITE_CACHE = {}


class CurrentSiteMiddleware(MiddlewareMixin):
    """
    Middleware that sets `site` attribute to request object.
    """

    def process_request(self, request):
        request.site = self.get_current_site(request)
        request.template = request.site.siteproperty.template if request.site.siteproperty.template else request.site.name

    def get_current_site(self, request):
        from django.conf import settings
        if getattr(settings, 'SITE_ID', ''):
            site_id = settings.SITE_ID
            return self._get_site_by_id(site_id)
        elif request:
            return self._get_site_by_request(request)

    def _get_site_by_id(self, site_id):
        if site_id not in SITE_CACHE:
            site = Site.objects.get(pk=site_id)
            SITE_CACHE[site_id] = site
        return SITE_CACHE[site_id]

    def _get_site_by_request(self, request):
        host = request.get_host()
        try:
            # First attempt to look up the site by host with or without port.
            if host not in SITE_CACHE:
                SITE_CACHE[host] = Site.objects.get(domain__icontains=host)
            return SITE_CACHE[host]
        except Site.DoesNotExist:
            # Fallback to looking up site after stripping port from the host.
            domain, port = split_domain_port(host)
            if domain not in SITE_CACHE:
                SITE_CACHE[domain] = Site.objects.get(domain__icontains=domain)
            return SITE_CACHE[domain]
