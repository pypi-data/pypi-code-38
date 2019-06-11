# -*- coding: utf-8 -*-

import logging_helper
from ...base_template_support_api import TemplateBaseSupportApi

logging = logging_helper.setup_logging()


class TemplateApiV0(TemplateBaseSupportApi):
    PATH = u''

    def example(self):
        return self.get(request=u'',
                        timeout=self.SHORT_TIMEOUT)
