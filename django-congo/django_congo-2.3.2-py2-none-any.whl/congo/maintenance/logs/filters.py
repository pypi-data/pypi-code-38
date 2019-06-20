# -*- coding: utf-8 -*-
import logging
from congo.conf import settings

class IgnoreCommonErrors(logging.Filter):
    def filter(self, record):
        exc_text = getattr(record, 'exc_text', None)

#        settings.CONGO_COMMON_ERRORS_IGNORE_LIST = [
#            "AttributeError: 'NoneType' object has no attribute 'get_object_by_attrs'",
#            "ZeroDivisionError: integer division or modulo by zero",
#            "TypeError: argument of type 'NoneType' is not iterable",
#        ]

        return not any([e in exc_text for e in settings.CONGO_COMMON_ERRORS_IGNORE_LIST])

class IgnoreCommonWarnings(logging.Filter):
    def filter(self, record):

       settings.CONGO_COMMON_WARNINGS_IGNORE_LIST = [
           'RemovedInDjango20Warning',
       ]

       return not any([warning in record.getMessage() for warning in settings.CONGO_COMMON_WARNINGS_IGNORE_LIST])
