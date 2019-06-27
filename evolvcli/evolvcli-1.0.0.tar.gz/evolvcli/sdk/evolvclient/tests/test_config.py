import unittest

from ..config import EvolvConfig


class TestEvolvConfig(unittest.TestCase):
    """
    Tests the EvolvConfig class.
    """
    API_KEY = 'xx_test_xx'
    API_DOMAIN = 'test.evolv.ai'
    API_VERSION = 'xx'

    def test_create_instance(self):
        """
        Tests the creation of a EvolvConfig instance.
        """
        config = EvolvConfig(api_key=self.API_KEY,
                             api_domain=self.API_DOMAIN,
                             api_version=self.API_VERSION)
        self.assertIsInstance(config, EvolvConfig)
        self.assertEqual(config.api_key, self.API_KEY)
        self.assertEqual(config.api_domain, self.API_DOMAIN)
        self.assertEqual(config.api_version, self.API_VERSION)

    def test_change_sdk_key(self):
        """
        Tests the ability to change the sdk key of a EvolvConfig instance.
        """
        config = EvolvConfig(api_key=self.API_KEY)
        self.assertEqual(config.api_key, self.API_KEY)

        new_api_key = "67890"
        config.api_key = new_api_key
        self.assertEqual(config.api_key, new_api_key)


if __name__ == '__main__':
    unittest.main()
