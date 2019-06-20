# -*- coding: utf-8 -*-
from congo.templatetags.admin_utils import module_class_name
from django.core.cache import DEFAULT_CACHE_ALIAS, caches
from django.urls.base import reverse, resolve
from django.urls.exceptions import Resolver404, NoReverseMatch
from django.utils import translation
from django.utils.translation.trans_real import parse_accept_lang_header
from urlparse import urlparse
import hashlib
import re

language_code_re = re.compile(
    r'^[a-z]{1,8}(?:-[a-z0-9]{1,8})*(?:@[a-z0-9]{1,20})?$',
    re.IGNORECASE
)

def get_accept_language_from_request(request, default = ''):
    accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    for accept_lang, unused in parse_accept_lang_header(accept):
        if accept_lang == '*':
            break

        if not language_code_re.search(accept_lang):
            continue

        return accept_lang.split('-')[0]

    return default

def get_url_for_language(language, url_or_obj = None, **kwargs):
    md5 = hashlib.md5()
    url = None
    obj = None

    # calculate cache key
    if isinstance(url_or_obj, unicode):
        url_args = kwargs.get('url_args', [])
        url_kwargs = kwargs.get('url_kwargs', {})

        try:
            url = reverse(url_or_obj, args = url_args, kwargs = url_kwargs)
        except NoReverseMatch:
            url = url_or_obj
        md5.update(url)

        if url_args:
            for a in url_args:
                md5.update(str(a))

        if url_kwargs:
            for k, v in url_kwargs.items():
                md5.update(k)
                md5.update(str(v))

    elif hasattr(url_or_obj, 'id') and hasattr(url_or_obj, 'get_absolute_url'):
        obj = url_or_obj
        md5.update(str(obj.id))
        md5.update(module_class_name(obj))

    else:
        return None

    cache_key = "lang_url_%s_%s" % (language, md5.hexdigest()[:10])
    cache = caches[kwargs.get('cache_name', DEFAULT_CACHE_ALIAS)]

    # get from cache
    translated_url = cache.get(cache_key)

    # set to cache
    if translated_url is None:
        if obj:
            with translation.override(language):
                # @og wypadałoby obsłużyć sytuację, gdy obj nie jest przetłumaczony na dany język...
                translated_obj = type(obj).objects.get(id = obj.id)
                translated_url = translated_obj.get_absolute_url()
        else:
            try:
                view = resolve(urlparse(url)[2])
                with translation.override(language):
                    translated_url = reverse(view.view_name, args = view.args, kwargs = view.kwargs)
            except (Resolver404, NoReverseMatch):
                translated_url = False

        cache.set(cache_key, translated_url, timeout = kwargs.get('cache_timeout', 24 * 60 * 60))

    return translated_url
