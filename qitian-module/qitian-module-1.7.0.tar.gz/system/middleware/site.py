from django.utils.deprecation import MiddlewareMixin

from django.contrib.sites.models import Site
from django.http.request import split_domain_port
from system.models import SiteProperty
from django.conf import settings

SITE_CACHE = {}


class CurrentSiteMiddleware(MiddlewareMixin):
    """
    Middleware that sets `site` attribute to request object.
    """

    def process_request(self, request):
        request.site = self.get_current_site(request)
        SiteProperty.check_site_property(request.site)
        request.template = request.site.siteproperty.template if request.site.siteproperty.template else request.site.name

    def get_current_site(self, request):
        return self._get_site_by_request(request)
        # if getattr(settings, 'SITE_ID', ''):
        #     site_id = settings.SITE_ID
        #     return self._get_site_by_id(site_id)
        # elif request:
        #     return self._get_site_by_request(request)

    @staticmethod
    def _get_site_by_id(site_id):
        if site_id not in SITE_CACHE:
            site = Site.objects.get(pk=site_id)
            SITE_CACHE[site_id] = site
        return SITE_CACHE[site_id]

    @staticmethod
    def _get_site_by_request(request):
        """
        如果没有找到站点就显示第一个
        :param request:
        :return:
        """
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
                if Site.objects.filter(domain__icontains=domain).exists():
                    SITE_CACHE[domain] = Site.objects.get(domain__icontains=domain)
                else:
                    SITE_CACHE[domain] = Site.objects.get(pk=1)
                # if getattr(settings, 'SITE_ID', ''):
                settings.SITE_ID = SITE_CACHE[domain].id

            return SITE_CACHE[domain]
