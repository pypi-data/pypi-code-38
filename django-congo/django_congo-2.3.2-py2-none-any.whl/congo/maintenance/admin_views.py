# -*- coding: utf-8 -*-
from congo.utils.decorators import staff_required, secure_allowed
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render
from congo.conf import settings
from django.contrib import messages
import logging
import sys
from collections import OrderedDict
from django.utils import timezone
from django.core.cache import caches
from django.core.cache.backends.base import InvalidCacheBackendError
from django.http.response import HttpResponseRedirect

@secure_allowed
@staff_required
def clear_cache(request):
    title = _(u"Wyczyść cache")
    cache_name_list = settings.CACHES.keys()

    if request.method == 'POST':
        cache_name_list = request.POST.getlist('cache_name', [])
        logger = logging.getLogger('system.clear_cache')

        for cache_name in cache_name_list:
            if cache_name in cache_name_list:
                msg = u"%s: %s" % (title, cache_name)

                extra = {
                    'user': request.user,
                    'extra_info': OrderedDict(),
                }

                try:
                    start_time = timezone.now()
                    caches[cache_name].clear()
                    end_time = timezone.now()

                    messages.success(request, u"Cache %s został wyczyszczony." % cache_name)

                    extra['extra_info']['time'] = end_time - start_time
                    logger.info(msg, extra = extra)
                except InvalidCacheBackendError:
                    messages.error(request, u"Cache %s nie został wyczyszczony." % cache_name)

                    exc_info = sys.exc_info()
                    logger.error(msg, exc_info = exc_info, extra = extra)

        return HttpResponseRedirect(".")

    extra_context = {
        'title': title,
        'has_permission': True,
        'site_url': '/',

        'cache_name_list': cache_name_list,
    }

    return render(request, 'congo/admin/maintenance/clear_cache.html', extra_context)
