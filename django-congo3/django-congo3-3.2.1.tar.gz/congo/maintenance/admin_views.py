# -*- coding: utf-8 -*-
from collections import OrderedDict
from congo.conf import settings
from congo.maintenance import get_admin_model
from congo.utils.decorators import staff_required
from django.contrib import messages
from django.core.cache import caches
from django.core.cache.backends.base import InvalidCacheBackendError
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
import logging
import sys


@staff_required
def clear_cache(request):
    title = "Wyczyść cache"
    cache_name_list = list(settings.CACHES.keys())

    if request.method == 'POST':
        cache_name_list = request.POST.getlist('cache_name', [])
        logger = logging.getLogger('system.clear_cache')

        for cache_name in cache_name_list:
            if cache_name in cache_name_list:
                msg = "%s: %s" % (title, cache_name)

                extra = {
                    'user': request.user,
                    'extra_info': OrderedDict(),
                }

                try:
                    start_time = timezone.now()
                    caches[cache_name].clear()
                    end_time = timezone.now()

                    messages.success(request, "Cache %s został wyczyszczony." % cache_name)

                    extra['extra_info']['time'] = end_time - start_time
                    logger.info(msg, extra = extra)
                except InvalidCacheBackendError:
                    messages.error(request, "Cache %s nie został wyczyszczony." % cache_name)

                    exc_info = sys.exc_info()
                    logger.error(msg, exc_info = exc_info, extra = extra)

        return HttpResponseRedirect(".")

    AdminModel = get_admin_model()

    extra_context = {
        'title': title,
        'has_permission': True,
        'site_url': '/',

        'js_list': getattr(AdminModel.Media, 'js', []) if hasattr(AdminModel, 'Media') else [],

        'cache_name_list': cache_name_list,
    }

    return render(request, 'congo/admin/maintenance/clear_cache.html', extra_context)
