# -*- coding: utf-8 -*-
from collections import Sequence


def conditional_http_tween_factory(handler, registry):
    """
    Tween that adds ETag headers and tells Pyramid to enable 
    conditional responses where appropriate.
    """
    settings = registry.settings if hasattr(registry, 'settings') else {}
    not_cacheble_list = []
    if 'not.cachable.list' in settings:
        not_cacheble_list = settings.get('not.cachable.list').split()

    def conditional_http_tween(request):
        response = handler(request)

        if request.path not in not_cacheble_list:

            # If the Last-Modified header has been set, we want to enable the
            # conditional response processing.
            if response.last_modified is not None:
                response.conditional_response = True

            # We want to only enable the conditional machinery if either we
            # were given an explicit ETag header by the view or we have a
            # buffered response and can generate the ETag header ourself.
            if response.etag is not None:
                response.conditional_response = True
            elif (isinstance(response.app_iter, Sequence) and
                          len(response.app_iter) == 1) and response.body is not None:
                response.conditional_response = True
                response.md5_etag()

        return response

    return conditional_http_tween
