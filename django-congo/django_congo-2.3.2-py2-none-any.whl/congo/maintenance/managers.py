# -*- coding: utf-8 -*-
from django.db import models
from congo.maintenance import SITE_CACHE

class SiteManager(models.Manager):
    use_in_migrations = True

    def get_by_id(self, site_id):
        if site_id not in SITE_CACHE:
            site = self.get(pk = site_id)
            SITE_CACHE[site_id] = site
        return SITE_CACHE[site_id]

    def get_by_request(self, request):
        host = request.get_host()
        if host not in SITE_CACHE:
            site = self.get(domain__iexact = host)
            SITE_CACHE[host] = site
        return SITE_CACHE[host]

    def get_current(self, request = None):
        from django.conf import settings
        if getattr(settings, 'SITE_ID', ''):
            site_id = settings.SITE_ID
            return self.get_by_id(site_id)
        elif request:
            return self.get_by_request(request)
        else:
            return None

    def clear_cache(self):
        global SITE_CACHE
        SITE_CACHE = {}
