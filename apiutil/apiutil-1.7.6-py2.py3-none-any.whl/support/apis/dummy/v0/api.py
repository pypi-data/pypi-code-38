# -*- coding: utf-8 -*-

import logging_helper
from ...base_support_api import BaseSupportApi

logging = logging_helper.setup_logging()


class DummyApiV0(BaseSupportApi):

    PATH = u''

    def dummy(self,
              refresh=False):

        if not refresh:
            try:
                return self._dummy
            except AttributeError:
                pass

        try:
            self._dummy = self.get(request=u'',
                                   timeout=self.SHORT_TIMEOUT)
        except KeyError:
            self._dummy = []

        return self._dummy

    # These are just examples and will not do anything when called on the dummy API!
    def dummy_get(self):
        dummy_get = self.get(u'dummy_get',
                             timeout=self.SHORT_TIMEOUT)
        return dummy_get

    def dummy_ws(self,
                 **params):
        return self.ws_request(u'dummy_ws',
                               **params)
