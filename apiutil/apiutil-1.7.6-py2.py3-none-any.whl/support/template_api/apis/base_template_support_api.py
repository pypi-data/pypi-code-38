# -*- coding: utf-8 -*-

import logging_helper
from apiutil.support import BaseSupportApi

logging = logging_helper.setup_logging()


class TemplateBaseSupportApi(BaseSupportApi):

    # DOMAIN must be defined in subclass for versioned api's
    PATH = u''

    # This is only needed is you are actually going to overrider something otherwise just use BaseSupportApi
