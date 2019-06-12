from .Client import SchemaRegistryClient
from .Seliarizer import MessageSerializer
from kafka import KafkaConsumer
from kafka import KafkaProducer
import json

class SchemaRegistryLibrary():
    def _set_client(self, schemaRegistryUrl):
        client = SchemaRegistryClient(schemaRegistryUrl)
        return client

    def _set_serializer(self, schemaRegistryUrl):
        client = self._set_client(schemaRegistryUrl)
        serializer = MessageSerializer(client)
        return serializer

    def get_latest_schema_for_topic(self, schemaRegistryUrl, topic):
        client = self._set_client(schemaRegistryUrl)
        schma_id, avro_schema, version = client.get_latest_schema(topic)
        return avro_schema

    def encode_with_topic_name(self, schemaRegistryUrl, topic, record):
        serializer = self._set_serializer(schemaRegistryUrl)
        encoded = serializer.encode_record_for_topic(topic, record)
        return encoded

    def decode_message_with_schema_registry(self, schemaRegistryUrl, record):
        serializer = self._set_serializer(schemaRegistryUrl)
        message_decoded = serializer.decode_message(msg.value)
        return message_decoded

    def get_decoded_messages_from_topic(self,
                                topic,
                                schemaRegistryUrl,
                                bootstrap_servers,
                                client_id='Robot',
                                auto_offset_reset='earliest',
                                group_id=None,
                                enable_auto_commit=True,
                                consumer_timeout_ms=5000,
                                only_last_message=False):

        serializer = self._set_serializer(schemaRegistryUrl)
        allMessages = []
        consumer = KafkaConsumer(topic,
                                 bootstrap_servers=[bootstrap_servers],
                                 auto_offset_reset=auto_offset_reset,
                                 group_id=group_id,
                                 client_id=client_id,
                                 enable_auto_commit=enable_auto_commit,
                                 consumer_timeout_ms=consumer_timeout_ms)
        for msg in consumer:
                msg_value = msg.value
                message_decoded = serializer.decode_message(msg.value)
                allMessages.append(message_decoded)

        if only_last_message:
            return allMessages[-1]
        else:
            return allMessages

    def get_json_from_file(self, msg_path):
        with open(msg_path) as json_file:
            return json.loads(json_file.read())

    def send_message(self, bootstrap_servers, topic, message, client_id='Robot', timeout=50):
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers, client_id=client_id)
        future = producer.send(topic, value=message)
        future.get(timeout=timeout)
