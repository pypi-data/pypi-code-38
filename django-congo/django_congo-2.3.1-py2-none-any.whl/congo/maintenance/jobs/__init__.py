# -*- coding: utf-8 -*-
from collections import OrderedDict
from django.conf import settings
from django.utils import timezone, translation
from django.utils.translation import ugettext_lazy as _
from unidecode import unidecode
import logging
import os
import sys
from django.utils.encoding import force_text

class BaseJob(object):
    name = u"" # eg. clear_objects
    description = u"" # eg. Removing objects of class A and B older than 30 days
    can_import_settings = True

    def __init__(self):
        self.name = self.__module__.split('.')[-1]
        translation.activate(settings.LANGUAGE_CODE)

    def __str__(self):
        return self.name

    def _run(self, *args, **kwargs):
        raise NotImplementedError("The _run() method should take the one user argument (User), perform a task and return result (dict, SortedDict, OrderedDict).")

    def run(self, user, *args, **kwargs):
        logger = logging.getLogger('system.cron.%s' % self.name)

        exc_info = None
        extra = {
            'user': user,
            'extra_info': OrderedDict()
        }

        success = None

        start_time = timezone.now()
        try:
            result = self._run(user, *args, **kwargs)
            level = result.pop('level') if 'level' in result else logging.INFO
            message = result.pop('message') if 'message' in result else _(u"Zadanie wykonane")
            extra['extra_info'].update(result)
            success = True
        except Exception, e:
            level = logging.ERROR

            try:
                err = unicode(e)
            except UnicodeDecodeError:
                err = unicode(str(e).decode("WINDOWS-1250"))

            message = u"[%s] %s" % (e.__class__.__name__, err)
            exc_info = sys.exc_info()
            success = False
        end_time = timezone.now()
        extra['extra_info']['time'] = end_time - start_time

        logger.log(level, message, exc_info = exc_info, extra = extra)

        return success
