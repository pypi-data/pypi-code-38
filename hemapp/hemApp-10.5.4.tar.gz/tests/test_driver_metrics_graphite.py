import mock
import socket

def test_check_init():
    import hemApp
    metrics = hemApp.initialise_metrics({"type":"graphite"})
    assert hemApp.drivers.metrics_graphite.instance is type(metrics)

def test_check_stage():
    import hemApp
    metrics = hemApp.initialise_metrics({"type":"graphite"})
    length = len(metrics.cache) 
    metrics.stage('hello',1)
    assert len(metrics.cache) is length+1
    assert "hem.hello" in metrics.cache[length]

def test_check_prefix():
    import hemApp
    metrics = hemApp.initialise_metrics({"type":"graphite", "prefix":"nothem"})
    assert metrics.prefix == "nothem"
    metrics.stage('hello',1)
    assert "nothem." in metrics.cache[-1]
        