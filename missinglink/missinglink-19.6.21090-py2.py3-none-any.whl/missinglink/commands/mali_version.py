# -*- coding: utf-8 -*-
import os
from .self_update.sdk_version import get_version


class MissinglinkVersion(object):
    PACKAGE = 'missinglink'

    @classmethod
    def get_missinglink_cli_version(cls):
        return os.environ.get('_ML_FORCE_VERSION', get_version(cls.PACKAGE))

    @classmethod
    def get_missinglink_package(cls):
        return cls.PACKAGE
