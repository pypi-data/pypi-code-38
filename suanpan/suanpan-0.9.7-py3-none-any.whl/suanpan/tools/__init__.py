# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.docker import DockerComponent
from suanpan.log import logger


class ToolComponent(DockerComponent):
    ENABLED_BASE_SERVICES = {"dw", "storage"}

    def beforeInit(self):
        logger.logDebugInfo()
        logger.debug("ToolComponent {} starting...".format(self.name))

    def afterSave(self):
        logger.debug("ToolComponent {} done.".format(self.name))
