import pika

from rabbitholer.logger import debug, debug_cyan


class RabbitDumper:

    def __init__(self, exchange, queue, routing_key, server):

        self.exchange = exchange
        self.queue = queue
        self.routing_key = routing_key
        self.server = server

        self.callback = None

        debug_cyan('Trying to open connection to {}'.format(server))
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=server))
            debug('Connection opend')

            self.channel = self.connection.channel()
            self.channel.basic_qos(prefetch_count=1)

            self.channel.exchange_declare(exchange=self.exchange,
                                          exchange_type='fanout',
                                          passive=False,
                                          durable=False,
                                          auto_delete=False)
            debug('Declared exchange with name {}'.format(exchange))

            self.channel.queue_declare(queue=self.queue, auto_delete=False)
            debug('Declared queue with name {}'.format(queue))

            self.channel.queue_bind(exchange=self.exchange,
                                    queue=self.queue,
                                    routing_key=self.routing_key)
            debug('Queue was bound to the exchange')

        except pika.exceptions.ConnectionClosedByBroker as err:
            print("AMQP Connection closed by the broker: {}".format(err))
        except pika.exceptions.AMQPChannelError as err:
            print("AMQP channel error: {}, stopping...".format(err))
        except pika.exceptions.AMQPConnectionError as err:
            print("AMQP Connection closed: {}".format(err))

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.destroy()

    def new_msg(self, *args):
        debug_cyan('New message received: {}'
                   .format(args[3]))
        self.callback(args[3].decode("utf-8"))

    def send(self, msg):
        debug_cyan('Trying to send message: {}.'.format(msg))
        try:
            props = pika.spec.BasicProperties(expiration='30000')
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.routing_key,
                body=msg,
                properties=props)
            debug('Message send!')
        except pika.exceptions.ConnectionClosedByBroker as err:
            print("AMQP Connection closed by the broker: {}".format(err))
        except pika.exceptions.AMQPChannelError as err:
            print("AMQP channel error: {}, stopping...".format(err))
        except pika.exceptions.AMQPConnectionError as err:
            print("AMQP Connection closed: {}".format(err))

    def receive(self, callback):
        self.callback = callback
        debug_cyan('Starting to recieve messages from {}'
                   .format(self.queue))
        try:
            self.channel.basic_consume(
                queue=self.queue, on_message_callback=self.new_msg,
                auto_ack=True)
            self.channel.start_consuming()
        except pika.exceptions.ConnectionClosedByBroker as err:
            print("AMQP Connection closed by the broker: {}.".format(err))
        except pika.exceptions.AMQPChannelError as err:
            print("AMQP channel error: {}.".format(err))
        except pika.exceptions.AMQPConnectionError as err:
            print("AMQP Connection closed: {}.".format(err))

    def destroy(self):
        debug_cyan('Closing connection to the broker.')
        self.channel.close()
        self.connection.close()
