import pytest

from jkutils.jkafka import JKKafka

kafka_server = "172.16.1.206:9092"


@pytest.mark.skip(reason="skip")
def test_producer():
    client = JKKafka(bootstrap_servers=kafka_server)
    client.send(topic_name="test", data="test".encode("utf-8"))
    assert True
