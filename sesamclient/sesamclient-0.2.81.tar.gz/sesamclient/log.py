# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import logging

from . import utils
from .entitybase import EntityBase

logger = logging.getLogger(__name__)


class Log(EntityBase):
    """
    This class represents a logfile.
    """

    def __str__(self):
        result = super().__str__()
        return result

    def get_content(self):
        """This returns a stream with the actual logfile content"""
        return self._connection.get_log_content(self.id)
