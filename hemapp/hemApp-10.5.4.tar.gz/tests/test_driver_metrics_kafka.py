try:
    from unittest.mock import patch
except:
    from mock import patch

import pykafka
def test_check_init(mocker):
    import hemApp
    mocker.patch('pykafka.KafkaClient')
    metrics = hemApp.initialise_metrics({"type":"kafka"})
    assert hemApp.drivers.metrics_kafka.instance is type(metrics)
    assert pykafka.KafkaClient.called_once_with('localhost','9092')
    metrics.stage('test_metric', 100)
    assert pykafka.KafkaClient.called
