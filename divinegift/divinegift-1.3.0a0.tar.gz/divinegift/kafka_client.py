from kafka import KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import KafkaError


class ProducerNotSetError(Exception):
    pass


class ConsumerNotSetError(Exception):
    pass


class KafkaClient:
    def __init__(self, producer=None, consumer=None):
        """
        :param producer: KafkaProducer
        :type producer: KafkaProducer
        :param consumer: KafkaConsumer
        :type consumer: KafkaConsumer
        """
        self.producer = producer
        self.consumer = consumer

    def set_producer(self, **configs):
        self.producer = KafkaProducer(**configs)

    def close_producer(self):
        if self.producer:
            self.producer.close()
            self.producer = None
        else:
            raise ProducerNotSetError('Set consumer before!')

    def set_consumer(self, **configs):
        self.consumer = KafkaConsumer(**configs)

    def close_consumer(self):
        if self.consumer:
            self.consumer.close()
            self.consumer = None
        else:
            raise ConsumerNotSetError('Set consumer before!')

    def send_message(self, topic, messages):
        if self.producer:
            if isinstance(messages, list):
                for message in messages:
                    if not isinstance(message, bytes):
                        self.producer.send(topic, message.encode('utf-8'))
                    else:
                        self.producer.send(topic, message)
            else:
                if not isinstance(messages, bytes):
                    self.producer.send(topic, messages.encode('utf-8'))
                else:
                    self.producer.send(topic, messages)
            self.producer.flush()
        else:
            raise ProducerNotSetError('Set producer before!')

    def read_messages(self, topic, from_beginning=False):
        if self.consumer:
            messages = []
            # Read and print all messages from test topic
            self.consumer.assign([TopicPartition(topic, 0)])
            if from_beginning:
                self.consumer.seek_to_beginning(TopicPartition(topic, 0))
            for i, msg in enumerate(self.consumer):
                 messages.append(msg.value.decode('utf-8'))
            return messages
        else:
            raise ConsumerNotSetError('Set consumer before!')


if __name__ == '__main__':
    pass
