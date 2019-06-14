from __future__ import (absolute_import, division, print_function, unicode_literals)

import csv
import logging
import sys
import traceback

logger = logging.getLogger(__name__)
from .klass_connector import Connector


class CsvConnector(Connector):
    def get(self):
        self.params.pop('path', None)
        try:
            f = csv.DictReader(open(self.path, encoding='utf-8'), **self.params)
            logger.info('Loading the file [%s] is succeeded', self.path)
            return f
        except:
            logger.error('Loading the file [%s] is failed', self.path)
            logger.error(traceback.format_exc())
            sys.exit(-1)
