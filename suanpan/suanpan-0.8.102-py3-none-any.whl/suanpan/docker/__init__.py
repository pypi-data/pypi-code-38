# coding=utf-8
from __future__ import absolute_import, print_function

import itertools

from suanpan import g
from suanpan.components import Component
from suanpan.dw import dw
from suanpan.interfaces import HasDevMode, HasLogger
from suanpan.interfaces.optional import HasBaseServices
from suanpan.log import logger
from suanpan.mstorage import mstorage
from suanpan.storage import storage


class DockerComponent(Component, HasBaseServices, HasLogger, HasDevMode):
    ENABLED_BASE_SERVICES = {"dw", "storage", "mstorage"}

    def beforeInit(self):
        logger.logDebugInfo()
        logger.debug("DockerComponent {} starting...".format(self.name))

    def initBase(self, args):
        logger.setLogger(self.name)
        self.setBaseServices(args)

    def afterSave(self):
        logger.debug("DockerComponent {} done.".format(self.name))
