import unittest
import mock

def test_check_init():
    import hemApp
    hosts = hemApp.discover_hosts({
        "type":"file",
        "name":"hosts.yaml"})
    assert type(hosts) == list

def test_check_notfound():
    import hemApp
    try:
        with unittest.assertLogs(level='ERROR') as cm:
            hosts = hemApp.discover_hosts({
                "type":"file",
                "name":"notfound.nonexistent"})
        assert 'ERROR:hemApp.drivers.discovery_file:File not found' in cm.output
    except AttributeError:
        # self.assertLogs doesn't work in Python 2.x
        hosts = hemApp.discover_hosts({
            "type":"file",
            "name":"notfound.nonexistent"})
    except FileNotFoundError:
        assert False
    assert type(hosts) == list
    assert hosts == []

def test_check_content():
    import hemApp
    hosts = hemApp.discover_hosts({
        "type":"file",
        "name":"tests/hosts.yaml"})
    assert type(hosts) == list
    print(hosts)
    assert 'hostone' in hosts

def test_check_content_key():
    import hemApp
    hosts = hemApp.discover_hosts({
        "type":"file",
        "name":"tests/hosts_key.yaml",
        "key":"hostname"})
    assert type(hosts) == list
    print(hosts)
    assert 'host1.example.com' in hosts

def test_check_content_key_enable():
    import hemApp
    hosts = hemApp.discover_hosts({
        "type":"file",
        "name":"tests/hosts_key.yaml",
        "enabled_key":"check",
        "key":"hostname"})
    assert type(hosts) == list
    print(hosts)
    assert 'host0.example.com' not in hosts
    assert 'host1.example.com' in hosts
    assert 'host2.example.com' in hosts

def test_check_metrics(capsys):
    import hemApp
    metrics = hemApp.initialise_metrics({"type":"console"})
    discovery = {
        "type":"file",
        "name":"tests/hosts.yaml",
        "metrics": metrics}
    hemApp.discover_hosts(discovery)
    try:
        captured = capsys.readouterr()
        assert "discovery_file" in captured.out
    except AttributeError:
        print("Capsys not working in python 3.3 or 3.4 - investigating")
    
if __name__ == '__main__':
    unittest.main()
