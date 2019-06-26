# -*- coding: utf-8 -*-

import django.urls


def activity_inbox_middleware(get_response):
    def middleware(request):
        # setting request.urlconf doesn't work because that screws up
        # calls to reverse() within the normal django app
        if "application/activity+json" in request.META.get("HTTP_ACCEPT", ""):
            urlconf = "django_vox.activity_urls"
            resolver = django.urls.get_resolver(urlconf)
            resolver_match = resolver.resolve(request.path_info)
            callback, callback_args, callback_kwargs = resolver_match
            request.resolver_match = resolver_match

            return callback(request, *callback_args, **callback_kwargs)

        return get_response(request)

    return middleware
