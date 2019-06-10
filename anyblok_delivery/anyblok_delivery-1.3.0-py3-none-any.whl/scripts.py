# This file is a part of the AnyBlok / Delivery project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import anyblok
from anyblok_delivery.release import version
from anyblok.config import Configuration
from logging import getLogger

logger = getLogger(__name__)

Configuration.add_application_properties(
    'update_labels_status',
    [
        'logging',
        'dramatiq-broker',
    ],
    prog='AnyBlok update label status, version %r' % version,
    description="Update label status"
)


status = ['label', 'transit', 'exception']


def update_labels_status():
    """Execute a script or open an interpreter
    """
    registry = anyblok.start('update_labels_status')
    if registry:
        Shipment = registry.Delivery.Shipment
        query = Shipment.query()
        query = query.filter(Shipment.status.in_(status))
        for ship in query.all():
            try:
                ship.get_label_status()
            except Exception:
                logger.exception('failed to get label')

        registry.commit()
        registry.close()
