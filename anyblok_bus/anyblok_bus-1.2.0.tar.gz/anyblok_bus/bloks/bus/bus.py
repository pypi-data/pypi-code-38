# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Julien SZKUDLAPSKI <j.szkudlapski@sensee.com>
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.config import Configuration
from .exceptions import PublishException, TwiceQueueConsumptionException
from pika.exceptions import ChannelClosed
import logging
import pika

logger = logging.getLogger(__name__)


@Declarations.register(Declarations.Model)
class Bus:
    """ Namespace Bus """

    @classmethod
    def publish(cls, exchange, routing_key, data, contenttype):
        """Publish a message in an exchange with a routing key through
        rabbitmq with the profile given by the anyblok configuration

        :param exchange: name of the exchange
        :param routing_key: name of the routing key
        :param data: str or unitcode to send through rabbitmq
        :param contenttype: the mimestype of the data
        :exception: PublishException
        """
        profile_name = Configuration.get('bus_profile')
        channel = _connection = None
        try:
            with cls.registry.begin_nested():  # savepoint
                profile = cls.registry.Bus.Profile.query().filter_by(
                    name=profile_name
                ).one_or_none()
                parameters = pika.URLParameters(profile.url.url)
                _connection = pika.BlockingConnection(parameters)
                channel = _connection.channel()
                channel.confirm_delivery()
                try:
                    channel.basic_publish(
                        exchange=exchange,
                        routing_key=routing_key,
                        body=data,
                        properties=pika.BasicProperties(
                            content_type=contenttype, delivery_mode=1)
                    )
                    logger.info("Message published %r->%r",
                                exchange, routing_key)
                except pika.exceptions.UnroutableError:
                    raise PublishException("Message cannot be published")
        except Exception as e:
            logger.error("publishing failed with : %r", e)
            raise
        finally:
            if channel and not channel.is_closed:
                channel.close()
            if _connection and not _connection.is_closed:
                _connection.close()

    @classmethod
    def get_consumers(cls):
        """Return the list of the consumers"""
        grouped_consumers = []
        consumers = []
        queues = []
        for Model in cls.registry.loaded_namespaces.values():
            for queue, consumer, processes in Model.bus_consumers:
                if queue in queues:
                    raise TwiceQueueConsumptionException(
                        "The consumation of the queue %r is already defined" % (
                            queue))

                queues.append(queue)
                if processes == 0:
                    grouped_consumers.append(
                        (queue, Model.__registry_name__, consumer))
                else:
                    consumers.append((processes, [
                        (queue, Model.__registry_name__, consumer)]))

        if grouped_consumers:
            consumers.append(
                (Configuration.get('bus_processes', 1), grouped_consumers))

        return consumers

    @classmethod
    def get_unexisting_queues(cls):
        profile_name = Configuration.get('bus_profile')
        profile = cls.registry.Bus.Profile.query().filter_by(
            name=profile_name
        ).one_or_none()
        parameters = pika.URLParameters(profile.url.url)
        connection = pika.BlockingConnection(parameters)
        unexisting_queues = []
        for processes, definitions in cls.get_consumers():
            for queue, Model, consumer in definitions:
                channel = connection.channel()
                try:
                    channel.queue_declare(queue, passive=True)
                    channel.close()
                except ChannelClosed as exc:
                    if exc.args[0] == 404:
                        unexisting_queues.append(queue)
                        logger.warning(
                            "The queue %r consumed by '%s:%s' "
                            "does not exist on %r",
                            queue, Model, consumer, profile)

                    else:
                        raise

        connection.close()
        return unexisting_queues
