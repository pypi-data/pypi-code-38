import requests

def test_check_init():
    import hemApp
    metrics = hemApp.initialise_metrics({"type":"prometheus", "port":12345})
    assert hemApp.drivers.metrics_prometheus.instance is type(metrics)

def test_check_stage(capsys):
    import hemApp
    metrics = hemApp.initialise_metrics({"type":"prometheus", "port":12346})
    metrics.stage('hello',1)
    t = requests.get('http://localhost:12346').text
    assert 'hello' in t