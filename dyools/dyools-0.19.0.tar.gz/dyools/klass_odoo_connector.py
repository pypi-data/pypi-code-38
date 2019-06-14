from __future__ import (absolute_import, division, print_function, unicode_literals)

import logging
import sys
import traceback

import odoorpc

logger = logging.getLogger(__name__)
from .klass_connector import Connector


class OdooConnector(Connector):
    def get(self):
        try:
            hash_pwd = '{}****{}'.format(self.password[0], self.password[-1])
            self.hash_pwd = hash_pwd
            connection_str = '{s.host}:{s.port}/?dbname={s.dbname}&user={s.user}&password={s.hash_pwd}'.format(s=self)
            odoo = odoorpc.ODOO(host=self.host, port=self.port)
            odoo.login(self.dbname, self.user, self.password)
            logger.info('connection successful to %s', connection_str)
            return odoo
        except:
            logger.error('connection failed to %s', connection_str)
            logger.error(traceback.format_exc())
            sys.exit(-1)
