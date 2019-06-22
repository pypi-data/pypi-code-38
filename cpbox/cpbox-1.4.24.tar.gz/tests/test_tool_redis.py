import unittest
from cpbox.tool import redistool

class TestToolRedis(unittest.TestCase):

    def setUp(self):
        url = 'redis://:%s@%s:%s' % ('cp', '172.16.1.102', '10301')
        redistool.init_proxy(url)

    def test_get_kv(self):
        k = 'test'
        v = {'test': 'test'}
        value = redistool.get(k)
        self.assertEqual(value, None)

        redistool.set(k, v)
        value = redistool.get(k)
        self.assertEqual(value, v)
        redistool.delete(k)
        value = redistool.get(k)
        self.assertEqual(value, None)

    def test_get_list(self):
        key_list = []
        key_list.append('test1')
        key_list.append('test3')
        key_list.append('test2')
        redistool.delete_keys(key_list)
        value_list = redistool.get_list(key_list)
        self.assertTrue(not value_list)

        kv_list = {}
        kv_list['test1'] = {'test1': 'test1'}
        kv_list['test3'] = {'test3': 'test3'}
        kv_list['test2'] = {'test2': 'test2'}
        redistool.set_list(kv_list)

        want_value = {'test3': {'test3': 'test3'}, 'test1': {'test1': 'test1'}, 'test2': {'test2': 'test2'}}
        value_list = redistool.get_list(key_list)
        self.assertEqual(want_value, value_list)

        redistool.delete_keys(key_list)
        value_list = redistool.get_list(key_list)
        self.assertTrue(not value_list)

if __name__ == '__main__':
    unittest.main()
