# -*- coding: utf-8 -*-
import os

from missinglink.commands.utilities import pip_utils


class MissinglinkVersion(object):
    PACKAGE = 'missinglink'

    @classmethod
    def get_missinglink_cli_version(cls):
        return os.environ.get('_ML_FORCE_VERSION', pip_utils.installed_version(cls.PACKAGE))

    @classmethod
    def get_missinglink_package(cls):
        return cls.PACKAGE
