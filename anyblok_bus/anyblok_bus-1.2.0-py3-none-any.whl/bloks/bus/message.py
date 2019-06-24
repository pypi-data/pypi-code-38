# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Julien SZKUDLAPSKI <j.szkudlapski@sensee.com>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.column import Integer, String, LargeBinary, Text, DateTime
from anyblok_bus.status import MessageStatus
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@Declarations.register(Declarations.Model.Bus)
class Message:
    id = Integer(primary_key=True)
    create_date = DateTime(nullable=False, default=datetime.now)
    edit_date = DateTime(nullable=False, default=datetime.now,
                         auto_update=True)
    content_type = String(default='application/json', nullable=False)
    message = LargeBinary(nullable=False)
    sequence = Integer(default=100, nullable=False)
    error = Text()
    queue = String(nullable=False)
    model = String(nullable=False)
    method = String(nullable=False)

    def consume(self):
        """Try to consume on message to import it in database"""
        logger.info('consume %r', self)
        error = ""
        try:
            Model = self.registry.get(self.model)
            savepoint = self.registry.begin_nested()
            status = getattr(Model, self.method)(
                body=self.message.decode('utf-8'))
            savepoint.commit()
        except Exception as e:
            savepoint.rollback()
            logger.exception('Error while trying to consume message %r',
                             self.id)
            status = MessageStatus.ERROR
            error = str(e)

        if status is MessageStatus.ERROR or status is None:
            logger.info('%s Finished with an error %r', self, error)
            self.error = error
        else:
            self.delete()

    @classmethod
    def consume_all(cls):
        """Try to consume all the message, ordered by the sequence"""
        query = cls.query().order_by(cls.sequence)
        for consumer in query.all():
            try:
                consumer.consume()
            except Exception:
                pass
