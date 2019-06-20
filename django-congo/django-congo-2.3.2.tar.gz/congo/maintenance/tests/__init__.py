# -*- coding: utf-8 -*-
from collections import OrderedDict
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from unidecode import unidecode
import logging
import os
import sys

@python_2_unicode_compatible
class BaseTest(object):
    name = u"" # eg. old_debug_log_test
    description = u"" # eg. Checks if there are any DEBUG level logs older than 30 days

    def __init__(self):
        self.name = self.__module__.split('.')[-1]
        self.description = u"%s test done" % self.name

    def __str__(self):
        return self.name

    def _run(self, *args, **kwargs):
        raise NotImplementedError("The _run() method should take the one user argument (User), perform a task and return result (dict or OrderedDict).")

    def run(self, user, *args, **kwargs):
        logger = logging.getLogger('system.audit.%s' % self.name)

        result = {
            'result': None,
            'details': "",
        }

        exc_info = None
        extra = {
            'user': user,
            'extra_info': OrderedDict()
        }

        success = None

        start_time = timezone.now()
        try:
            result.update(self._run(*args, **kwargs))
            level = result.pop('level') if 'level' in result else logging.INFO
            message = result.pop('message') if 'message' in result else _(u"Test zakończony")
            success = True
        except Exception, e:
            level = logging.ERROR
            message = u"[%s] %s" % (e.__class__.__name__, e)
            exc_info = sys.exc_info()
            success = False
        end_time = timezone.now()
        extra['extra_info'].update(result)
        extra['extra_info']['time'] = end_time - start_time

        logger.log(level, message, exc_info = exc_info, extra = extra)

        return success, result
