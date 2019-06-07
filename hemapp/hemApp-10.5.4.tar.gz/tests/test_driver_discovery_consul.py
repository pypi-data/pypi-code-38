import unittest
import requests_mock


class Basics(unittest.TestCase):
        def test_check_init(self):
            import hemApp
            with requests_mock.mock() as m:
                m.get('http://1.1.1.1:8500/v1/catalog/service/testing', text="""
[
  {
    "ID": "40e4a748-2192-161a-0510-9bf59fe950b5",
    "Node": "foobar",
    "Address": "192.168.10.10",
    "Datacenter": "dc1",
    "TaggedAddresses": {
      "lan": "192.168.10.10",
      "wan": "10.0.10.10"
    },
    "NodeMeta": {
      "somekey": "somevalue"
    },
    "CreateIndex": 51,
    "ModifyIndex": 51,
    "ServiceAddress": "172.17.0.3",
    "ServiceEnableTagOverride": false,
    "ServiceID": "32a2a47f7992:nodea:5000",
    "ServiceName": "foobar",
    "ServicePort": 5000,
    "ServiceTags": [
      "tacos"
    ]
  }
]""")
                hosts = hemApp.discover_hosts({
                    "type":"consul",
                    "server":"1.1.1.1",
                    "name":"testing"})
                self.assertEqual(type(hosts), list)
                self.assertTrue("192.168.10.10:5000" in hosts)

if __name__ == '__main__':
    unittest.main()