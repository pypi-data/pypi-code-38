# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Count http codes for flask framework
"""
import logging

from ..rules import RuleCallback

LOGGER = logging.getLogger(__name__)


class CountHTTPCodesCBPHP(RuleCallback):
    def post(self, original, response, *args, **kwargs):
        """ Recover the status code and update the http_code metric
        """
        status_code = response["http_code"]
        self.record_observation("http_code", str(status_code), 1)

        return {}
