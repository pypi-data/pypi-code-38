from ..utils.event_hook import EventHook
from .kafka_manager import KafkaManager
from pykafka.exceptions import ConsumerStoppedException
from pykafka.common import OffsetType;
import logging
import math


class ConsumerManager(KafkaManager):
    def __init__(self, kafka_topic, kafka_host, exclude_internal_topics, reset_offset_on_start, offset_type, consumer_group, avro_helper_key, avro_helper_value, handle_message, ssl_config):
        super().__init__(kafka_topic, kafka_host, exclude_internal_topics, avro_helper_key, avro_helper_value, ssl_config)

        self.reset_offset_on_start = reset_offset_on_start
        self.consumer_group = consumer_group.encode('utf-8')
        self.simple_consumer = None

        if (offset_type=="LATEST"):
            self.auto_offset_reset = OffsetType.LATEST
        else:
            self.auto_offset_reset = OffsetType.EARLIEST

        # We create the simple consumer with the options
        self.simple_consumer = self.client_topic.get_simple_consumer(auto_commit_enable=True,
                                                                     auto_commit_interval_ms=10,
                                                                     reset_offset_on_start=self.reset_offset_on_start,
                                                                     auto_offset_reset=self.auto_offset_reset,
                                                                     consumer_id=self.consumer_group,
                                                                     consumer_group=self.consumer_group)

        # self.simple_consumer._consumer_id = self.consumer_group;
        # The emisor handler will be fired if a message is listened
        self.on_message = EventHook()
        if handle_message:
            self.on_message += handle_message

    # Listen to all messages with the specified options
    def listen_messages(self):
        try:
            for message in self.simple_consumer:
               self.decode_and_fire(message)

        # We do not throw the exception if it occurs because we have externally closed the simple consumer
        except ConsumerStoppedException as e:
            logging.warning("kafka consumer for topic " + str(self.topic) + "was stoped")

    # Listen to the last messages (specifying number) with the specified options
    def listen_last_messages(self, messages_number):
        MAX_PARTITION_REWIND = int(math.ceil(messages_number / len(self.simple_consumer._partitions)))
        # find the beginning of the range we care about for each partition
        offsets = [(p, op.last_offset_consumed - MAX_PARTITION_REWIND)
                   for p, op in self.simple_consumer._partitions.iteritems()]
        # if we want to rewind before the beginning of the partition, limit to beginning
        offsets = [(p, (o if o > -1 else -2)) for p, o in offsets]
        # reset the consumer's offsets
        self.simple_consumer.reset_offsets(offsets)
        try:
            for message in self.simple_consumer:
                self.decode_and_fire(message)
                # self.simple_consumer.commit_offsets()

        # We do not throw the exception if it occurs because we have externally closed the simple consumer
        except ConsumerStoppedException as e:
            logging.warning("kafka consumer for topic " + str(self.topic) + "was stoped")

    # We decode and pass the message to the handler
    def decode_and_fire(self, message):
        if message is not None:
            decoded_value, decoded_key = "", ""

            if self.avro_helper_key:
                decoded_key = self.avro_helper_key.avro_decode_message(message.partition_key)

            if self.avro_helper_value:
                decoded_value = self.avro_helper_value.avro_decode_message(message.value)
            decoded_message = {"decoded_key": decoded_key, "decoded_value": decoded_value}
            # We fire the handler to pass the decoded message
            self.on_message.fire(decoded_message)

    def stop(self):
        if self.simple_consumer:
            self.simple_consumer.stop()
            # self.simple_consumer.commit_offsets()
