# -*- coding: utf-8 -*-
from kafka import KafkaProducer


class JKKafka:
    def __init__(
        self,
        bootstrap_servers,
        sasl_mechanism=None,
        security_protocol="PLAINTEXT",
        sasl_plain_username=None,
        sasl_plain_password=None,
        **kwargs,
    ):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            sasl_mechanism=sasl_mechanism,
            security_protocol=security_protocol,
            sasl_plain_username=sasl_plain_username,
            sasl_plain_password=sasl_plain_password,
            **kwargs,
        )

    def send(self, topic_name, data: bytes, **kwargs):
        self.producer.send(topic=topic_name, value=data, **kwargs)

    def close(self):
        self.producer.close()
