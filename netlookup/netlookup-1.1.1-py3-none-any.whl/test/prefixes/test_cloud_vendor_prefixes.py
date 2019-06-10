
import json
import os
import tempfile
import unittest

from netlookup.prefixes import CloudNetworks

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
TEST_DATA_PREFIX_LEN = 25712
TEST_NETWORK_ADDRESSES = (
    {
        'address': '8.34.208.0',
        'network': '8.34.208.0/20',
    },
    {
        'address': '8.34.223.10',
        'network': '8.34.208.0/20',
    },
    {
        'address': '8.34.223.254',
        'network': '8.34.208.0/20',
    },
    {
        'address': '8.34.223.255',
        'network': '8.34.208.0/20',
    },
    {
        'address': '8.34.224.0',
    },
    {
        'address': '2c0f:fb50:4000::0',
        'network': '2c0f:fb50:4000::/36'
    },
    {
        'address': '2c0f:fb50:4000::10',
        'network': '2c0f:fb50:4000::/36'
    },
    {
        'address': '2c0f:fb50:4fff:ffff:ffff:ffff:ffff:fffe',
        'network': '2c0f:fb50:4000::/36'
    },
    {
        'address': '2c0f:fb50:4fff:ffff:ffff:ffff:ffff:ffff',
        'network': '2c0f:fb50:4000::/36'
    },
    {
        'address': '2c0f:fb50:5000::0'
    }
)
TEST_JSON_REQUIRED_FIELDS = ('type', 'cidr')
TEST_FILTER_COUNTS = {
    'invalidvalue': 0,
    'aws': 1360,
    'azure': 14621,
    'gcp': 9556,
    'google': 175,
}


class TestCloudVendorPrefixes(unittest.TestCase):
    """
    Test loading prefix data from a snapshot of actual data
    """

    def setUp(self) -> None:
        self.tempdir = None

    def tearDown(self) -> None:
        """
        Cleanup temporary test directory after test
        """
        if self.tempdir is not None and os.path.isdir(self.tempdir):
            try:
                for filename in os.listdir(self.tempdir):
                    os.unlink(os.path.join(self.tempdir, filename))
            except Exception as e:
                print('Error removing files in temporary directory {}: {}'.format(self.tempdir, e))

            try:
                os.rmdir(self.tempdir)
            except Exception as e:
                print('Error removing temporary directory {}: {}'.format(self.tempdir, e))

    def test_cloud_vendor_networks_no_data(self) -> None:
        """
        Test creating networks with no data using new temporary directory
        """
        self.tempdir = tempfile.mkdtemp()
        data = CloudNetworks(cache_directory=self.tempdir)
        self.assertEqual(len(data.networks), 0)

    def disabled_test_cloud_vendor_networks_updating(self) -> None:
        """
        Test updating test data from network. This test case requires internet connection
        """
        self.tempdir = tempfile.mkdtemp()
        data = CloudNetworks(cache_directory=self.tempdir)
        data.update()
        self.assertFalse(len(data.networks) == 0)

    def test_cloud_vendor_networks_loading(self) -> None:
        """
        Test creating networks with test data, ensuring correct number of networks is loaded
        """
        data = CloudNetworks(cache_directory=DATA_PATH)
        self.assertEqual(len(data.networks), TEST_DATA_PREFIX_LEN)

    def test_cloud_vendor_prefix_filtering(self):
        """
        Test filtering networks
        """
        data = CloudNetworks(cache_directory=DATA_PATH)
        for name, count in TEST_FILTER_COUNTS.items():
            matches = data.filter_type(name)
            self.assertEqual(len(matches), count, 'Mismatch in {} count {} != {}'.format(
                name,
                len(matches),
                count
            ))

    def test_cloud_vendor_prefix_lookup(self):
        """
        Test looking up networks from test data
        """
        data = CloudNetworks(cache_directory=DATA_PATH)
        for testcase in TEST_NETWORK_ADDRESSES:
            prefix = data.find(testcase['address'])
            network = testcase.get('network', None)
            if network is not None:
                self.assertIsNotNone(prefix, 'Error looking up address {}'.format(testcase['address']))
                self.assertEqual(str(prefix.cidr), network)
            else:
                self.assertIsNone(prefix)

    def test_cloud_vendor_json_formatting(self):
        """
        Test all loaded networks can be formatted as JSON
        """
        data = CloudNetworks(cache_directory=DATA_PATH)
        for prefix in data.networks:
            testdata = json.loads(json.dumps(prefix.as_dict()))
            for field in TEST_JSON_REQUIRED_FIELDS:
                self.assertTrue(field in testdata)
                self.assertIsNotNone(testdata[field])
