from ..utils.event_hook import EventHook
from .kafka_manager import KafkaManager
import datetime, time
import logging
import uuid


class ProducerManager(KafkaManager):
    def __init__(self, kafka_topic, kafka_host, exclude_internal_topics, client_id, send_messages_asynchronously,
                 avro_helper_key, avro_helper_value, successfully_sent_message, ssl_config):
        super().__init__(kafka_topic, kafka_host, exclude_internal_topics, avro_helper_key, avro_helper_value, ssl_config)

        self.client_id = client_id
        self.heartbeat_topic = b"system_heartbeat"

        # The emisor handler will be fired if a message is sent
        self.on_sent = EventHook()

        if successfully_sent_message and not (kafka_topic == self.heartbeat_topic):
            self.on_sent += successfully_sent_message

        if send_messages_asynchronously:
            self.producer = self.client_topic.get_producer()
            logging.info("Messages will be sent asynchronously")
        else:
            self.producer = self.client_topic.get_sync_producer()
            logging.info("Messages will be sent synchronously")

    def send_messages(self, messages: list):
        for m in messages:
            encoded_key, encoded_message = self._avro_encode(m)
            self.producer.produce(encoded_message, encoded_key)
            # We fire the handler to signify that the message was sent OK
            self.on_sent.fire(m)

    def _avro_encode(self, message):
        # Lazy people might just give the message itself as input
        if "message" not in message:
            message = {"message": message}
        # If our message has a key we use it, otherwise we use a default one
        if "key" not in message:
            date = datetime.datetime.utcnow()
            date_ms = int(time.mktime(date.timetuple())) * 1000
            # For the default key we set a RFC4122 version 4 compliant GUID
            message["key"] = {"distributionID": str(uuid.uuid4()), "senderID": self.client_id,
                              "dateTimeSent": date_ms, "dateTimeExpires": 0,
                              "distributionStatus": "Test", "distributionKind": "Unknown"}
        return (self.avro_helper_key.avro_encode_messages(message["key"]),
                self.avro_helper_value.avro_encode_messages(message["message"]))

    def stop(self):
        self.producer.stop()
