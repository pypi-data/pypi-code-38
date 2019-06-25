# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
"""Count HTTP codes for the aiohttp framework."""

import logging

from ..rules import RuleCallback

LOGGER = logging.getLogger(__name__)


class CountHTTPCodesCBAioHTTP(RuleCallback):
    def post(self, original, response, *args, **kwargs):
        """Recover the status code and update the http_code metric."""
        status_code = response.status
        self.record_observation("http_code", str(status_code), 1)
        return {}

    def failing(self, original, *args, **kwargs):
        """Recover the status code and update the http_code metric."""
        self.record_observation("http_code", "500", 1)
        return {}
