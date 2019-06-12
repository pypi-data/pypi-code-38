from avro import schema
from kafka import KafkaConsumer
from kafka import KafkaProducer
import json


def parse_schema_from_string(schema_str):
    """Parse a schema given a schema string"""
    return schema.Parse(schema_str)


def parse_schema_from_file(schema_path):
    """Parse a schema from a file path"""
    with open(schema_path) as f:
        return parse_schema_from_string(f.read())

# def get_json_from_file(msg_path):
#     with open(msg_path) as json_file:
#         return json.loads(json_file.read())
#
# def get_messages_from_topic(topic,
#                             bootstrap_servers,
#                             auto_offset_reset,
#                             group_id,
#                             client_id,
#                             enable_auto_commit,
#                             consumer_timeout_ms=5000):
#     allMessages = []
#     consumer = KafkaConsumer(topic,
#                              bootstrap_servers=[bootstrap_servers],
#                              auto_offset_reset=auto_offset_reset,
#                              group_id=group_id,
#                              client_id=client_id,
#                              enable_auto_commit=enable_auto_commit,
#                              consumer_timeout_ms=consumer_timeout_ms)
#     for msg in consumer:
#             msg_value = msg.value
#             message_decoded = serializer.decode_message(msg.value)
#             allMessages.append(message_decoded)
#     consumer.close()
#     return allMessages
#
# def send_message(bootstrap_servers, topic, message, client_id='Robot', timeout=50):
#     producer = KafkaProducer(bootstrap_servers=bootstrap_servers, client_id=client_id)
#     future = producer.send(topic, value=message)
#     future.get(timeout=timeout)
