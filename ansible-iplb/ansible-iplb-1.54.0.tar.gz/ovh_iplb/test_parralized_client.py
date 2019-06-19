import time
import unittest
from mock import Mock
from ovh_iplb.parralized_client import ParralizedClient


class ParralizedClientTest(unittest.TestCase):
    def setUp(self):
        self.base_client = Mock()
        self.p_client = ParralizedClient(self.base_client)
        self.random_args = (1, 2, 3)
        self.random_kwargs = {'a': 'a', 'b': 'b'}

    def test_put_should_directly_redirect_to_original_client(self):
        self.p_client.put(*self.random_args, **self.random_kwargs)
        self.base_client.put.assert_called_with(*self.random_args, **self.random_kwargs)

    def test_post_should_directly_redirect_to_original_client(self):
        self.p_client.post(*self.random_args, **self.random_kwargs)
        self.base_client.post.assert_called_with(*self.random_args, **self.random_kwargs)

    def test_get_should_directly_redirect_to_original_client(self):
        self.p_client.get(*self.random_args, **self.random_kwargs)
        self.base_client.get.assert_called_with(*self.random_args, **self.random_kwargs)

    def test_delete_should_directly_redirect_to_original_client(self):
        self.p_client.delete(*self.random_args, **self.random_kwargs)
        self.base_client.delete.assert_called_with(*self.random_args, **self.random_kwargs)

    def test_multiget_with_no_fail(self):
        def side_effect(path):
            return path

        self.base_client.get.side_effect = side_effect

        paths = ['a', 'b', 'c']
        self.assertEqual(self.p_client.multiget(paths), paths)
        for path in paths:
            self.base_client.get.assert_any_call(path)

    def test_multiget_with_one_fail(self):
        def side_effect(path):
            if path == 'c':
                raise RuntimeError('Unknown path')

        self.base_client.get.side_effect = side_effect

        paths = ['a', 'c']
        with self.assertRaises(RuntimeError, msg='Unknown path'):
            self.p_client.multiget(paths)

        for path in paths:
            self.base_client.get.assert_any_call(path)

    def test_multiget_with_timeout(self):
        def side_effect(path):
            if path == 'c':
                time.sleep(100)

        self.base_client.get.side_effect = side_effect

        paths = ['c']
        self.p_client.timeout_per_call = 0.01
        with self.assertRaises(RuntimeError, msg='time out'):
            self.p_client.multiget(paths)


if __name__ == '__main__':
    unittest.main()
