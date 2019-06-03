import pika

import message


class PikaMessage:
    """A wrapper around a Pika message.

    In the pika library, a message comes in three parts: A body, a
    properties object, and when reading, a delivery info object.
    This class bundles those three things together."""

    def __init__(
        self,
        body,
        properties=pika.BasicProperties,
        delivery_info=pika.spec.Basic.GetOk,
        ):
        """
        Create an instance.
        args:
          delivery_info [pika.spec.GetOK]
          properties [pika.spec.BasicProperties]
          body [str]
        """
        self.delivery_info = delivery_info
        self.properties = properties
        self.body = body

    def to_message(self):
        """Convert to the library's standard Message class."""
        msg = message.Message()
        msg.body = self.body
        msg.properties = {
            "content_type": self.properties.content_type,
            "content_encoding": self.properties.content_encoding,
            "headers": self.properties.headers,
            "delivery_mode": self.properties.delivery_mode,
            "priority": self.properties.priority,
            "correlation_id": self.properties.correlation_id,
            "reply_to": self.properties.reply_to,
            "expiration": self.properties.expiration,
            "message_id": self.properties.message_id,
            "timestamp": self.properties.timestamp,
            "type": self.properties.type,
            "user_id": self.properties.user_id,
            "app_id": self.properties.app_id,
            "cluster_id": self.properties.cluster_id,
            }
        msg.delivery_info = {
            "delivery_tag": self.delivery_info.delivery_tag
        }
        return msg
