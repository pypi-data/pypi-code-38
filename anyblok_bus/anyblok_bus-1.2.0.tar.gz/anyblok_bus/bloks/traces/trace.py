# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Julien SZKUDLAPSKI <j.szkudlapski@sensee.com>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.column import Integer, String, LargeBinary, Json, DateTime
from anyblok_bus.status import MessageStatus
from datetime import datetime
import logging
from anyblok_bus import bus_consumer

logger = logging.getLogger(__name__)


@Declarations.register(Declarations.Model.Bus)
class Trace:
    id = Integer(primary_key=True)
    create_date = DateTime(nullable=False, default=datetime.now)
    edit_date = DateTime(nullable=False, default=datetime.now,
                         auto_update=True)
    message = LargeBinary(nullable=False)
    properties = Json(nullable=False)
    queue = String()

    @bus_consumer(queue_name='firehose', with_properties=True)
    def consume_firehose(cls, body=None, properties=None):
        cls.insert(
            message=body.encode('utf-8'),
            queue='firehose',
            properties=properties)
        return MessageStatus.ACK
