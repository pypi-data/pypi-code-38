# This file is a part of the AnyBlok / Delivery project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.blok import Blok
from anyblok_delivery.release import version
from sqlalchemy.engine.reflection import Inspector
from logging import getLogger
logger = getLogger(__name__)


class DeliveryBlok(Blok):
    """Delivery blok
    """
    version = version
    author = "Franck BRET"
    required = ['attachment', 'address', 'anyblok-mixins']

    def pre_migration(self, latest_version):
        if latest_version is None:
            return

        if latest_version < '1.2.0':
            table = self.registry.migration.table('delivery_shipment')
            inspector = Inspector(self.registry.migration.conn)
            for check in inspector.get_check_constraints('delivery_shipment'):
                if check['name'].startswith('anyblok_ck_d_shipment__status_'):
                    table.check(check['name']).drop()

            logger.info('Start migration to rename status returned')
            self.registry.execute("""
                UPDATE delivery_shipment
                SET status = 'error'
                WHERE status = 'returned';
            """)
            logger.info('Migration finished to rename status')

    @classmethod
    def import_declaration_module(cls):
        from . import delivery # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import delivery
        reload(delivery)
