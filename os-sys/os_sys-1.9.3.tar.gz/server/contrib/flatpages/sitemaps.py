from server.apps import apps as server_apps
from server.contrib.sitemaps import Sitemap
from server.core.exceptions import ImproperlyConfigured


class FlatPageSitemap(Sitemap):
    def items(self):
        if not server_apps.is_installed('server.contrib.sites'):
            raise ImproperlyConfigured("FlatPageSitemap requires server.contrib.sites, which isn't installed.")
        Site = server_apps.get_model('sites.Site')
        current_site = Site.objects.get_current()
        return current_site.flatpage_set.filter(registration_required=False)
