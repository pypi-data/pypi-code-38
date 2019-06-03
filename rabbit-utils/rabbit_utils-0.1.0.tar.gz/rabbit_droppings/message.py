import pika

import pika_message


class Message:
    """Abstract representation of a RabbitMQ message.  It is independant of pika
    or any other library.
    
    The message has three parts: two dictionaries and a string:
    
    * body (string)
    
    * delivery_info (dict)
      * delivery_tag
    
    * properties (dict)
      * content_encoding
      * headers
      * delivery_mode
      * priority
      * correlation_id
      * reply_to
      * expiration
      * message_id
      * timestamp
      * type
      * user_id
      * app_id
      * cluster_id
    
    """

    def __init__(self,
                 body='',
                 delivery_info=None,
                 properties=None):
        """
        Create an instance.
        Args:
          body [str]
          delivery_info [dict]
          properties [dict]
        """
        self.body = body
        if delivery_info is None:
            delivery_info = {}
        if properties is None:
            properties = {}
        self.delivery_info = delivery_info
        self.properties = properties

    def attrs(self):
        return self.__dict__

    def to_message(self):
        return self

    def to_pika_message(self):
        delivery_info = pika.spec.Basic.GetOk(
            delivery_tag=self.delivery_info.get('delivery_tag')
            )
        properties = pika.spec.BasicProperties(
            content_type=self.properties.get('content_type'),
            content_encoding=self.properties.get('content_encoding'),
            headers=self.properties.get('headers'),
            delivery_mode=self.properties.get('delivery_mode'),
            priority=self.properties.get('priority'),
            correlation_id=self.properties.get('correlation_id'),
            reply_to=self.properties.get('reply_to'),
            expiration=self.properties.get('expiration'),
            message_id=self.properties.get('message_id'),
            timestamp=self.properties.get('timestamp'),
            type=self.properties.get('type'),
            user_id=self.properties.get('user_id'),
            app_id=self.properties.get('app_id'),
            cluster_id=self.properties.get('cluster_id'),
            )
        body = self.body
        return pika_message.PikaMessage(body,
                                        properties=properties,
                                        delivery_info=delivery_info)

