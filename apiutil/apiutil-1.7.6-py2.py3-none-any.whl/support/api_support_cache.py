# -*- coding: utf-8 -*-

import os
import logging_helper
from collections import OrderedDict
from timingsutil import ONE_WEEK
from configurationutil import Configuration
from cachingutil import (SimpleMemoryCache,
                         TwoLevelCache)
from apiutil.json_api import JsonApiRequestResponseFileCache

logging = logging_helper.setup_logging()


class SupportAPIFileCache(JsonApiRequestResponseFileCache):

    OBJECT_PAIRS_HOOK = OrderedDict

    def key(self,
            api,
            method,
            request,
            cache_host,
            cache_host_enable=True,
            cache_key_suffix=None,
            **_):

        """

        :param api:                 API that called the cache, Passed by API cache belongs to.
        :param method:              GET/POST etc, Passed by API cache belongs to.
        :param request:             The request path to cache response from, Passed by API cache belongs to.
        :param cache_host:          The host response is being retrieved from, Passed by API cache belongs to.
        :param cache_host_enable:   True if cache is host specific, False if shared, default=True.
        :param cache_key_suffix:    An additional string to add to key.
        :return:
        """

        key = u'{host}/{method}/{api}/{request}'.format(host=u'{host}'.format(host=cache_host)
                                                        if cache_host_enable else u'Shared',
                                                        method=method,
                                                        api=api.PATH,
                                                        request=request if request else u'_root_path')

        if cache_key_suffix is not None:
            key += u'/{suffix}'.format(suffix=cache_key_suffix)

        return u'{key}.json'.format(key=key)

    def fetch_from_source(self,
                          api,
                          **params):
        return api.make_api_request(**params)

    def pre_fetch_tasks(self,
                        **params):
        self.clear_expired_items_from_cache()


class SupportAPIMemoryCache(SimpleMemoryCache):

    def pre_fetch_tasks(self,
                        **params):
        self.clear_expired_items_from_cache()


class SupportAPIDualCache(TwoLevelCache):

    def __init__(self,
                 api_name,
                 max_age=ONE_WEEK):
        super(SupportAPIDualCache, self).__init__(transient_cache=SupportAPIMemoryCache,
                                                  persistent_cache=SupportAPIFileCache,
                                                  max_age=max_age,
                                                  folder=os.path.join(Configuration().cache_path,
                                                                      u'APIs'),
                                                  sub_folder=api_name)
