import unittest
from cpbox.tool import cache
from cpbox.tool import redistool
from cpbox.tool import local_cache
import random
import time

class TestToolredis(unittest.TestCase):

    def setUp(self):
        url = 'redis://:%s@%s:%s' % ('cp', '172.16.1.102', '10301')
        redistool.init_proxy(url)

    def test_fetch_list_from(self):
        test_result = {}

        times = 100
        ids = list(range(1, times))
        for id in ids:
            test_result[id] = random.random()

        def get_key_fn(id):
            return 'cache-test-from-' + str(id)

        def get_list_fn(ids):
            result_map = {}
            for id in ids:
                result_map[id] = test_result[id]
            return result_map

        keys = list(map(get_key_fn, ids))
        for key in keys:
            cache.delete(key)

        fetched_result = cache.fetch_list(ids, get_key_fn, get_list_fn, None, None, 600, True)
        for id, item in fetched_result.items():
            self.assertEqual(item[1], cache.FROM_SLOW_OP)

        fetched_result = cache.fetch_list(ids, get_key_fn, get_list_fn, None, None, 600, True)
        for id, item in fetched_result.items():
            if local_cache.cache_proxy.type == local_cache.CACHE_TYPE_EMPTY:
                self.assertEqual(item[1], cache.FROM_REDIS)
            else:
                self.assertEqual(item[1], cache.FROM_LOCAL_CACHE)

        fetched_result = cache.fetch_list(ids, get_key_fn, get_list_fn, None, None, 0, True)
        for id, item in fetched_result.items():
            self.assertEqual(item[1], cache.FROM_REDIS)
        for key in keys:
            cache.delete(key)

    def test_fetch_list_single(self):
        test_result = {}

        times = 100
        ids = list(range(1, times))
        for id in ids:
            test_result[id] = random.random()

        def get_key_fn(id):
            return 'cache-test-single-' + str(id)

        def get_list_fn(ids):
            result_map = {}
            for id in ids:
                result_map[id] = test_result[id]
            return result_map

        keys = list(map(get_key_fn, ids))

        for key in keys:
            cache.delete(key)

        fetched_result = cache.fetch_list(ids, get_key_fn, get_list_fn, None, None, 600)

        for _id in range(1, 1000):
            random_id = random.randint(1, times - 1)
            fetched_result = cache.fetch_list(random_id, get_key_fn, get_list_fn, None, None, 600)
            self.assertEqual(fetched_result, test_result[random_id])

        for key in keys:
            cache.delete(key)

    def test_fetch_list_batch(self):
        test_result = {}
        ids = list(range(1, 100))
        for id in ids:
            test_result[id] = random.random()

        def get_key_fn(id):
            return 'cache-test-batch' + str(id)

        def get_list_fn(ids):
            result_map = {}
            for id in ids:
                result_map[id] = test_result[id]
            return result_map

        keys = list(map(get_key_fn, ids))
        for key in keys:
            cache.delete(key)

        fetched_result = cache.fetch_list(ids, get_key_fn, get_list_fn, None, None, 600)
        self.assertEqual(fetched_result, test_result)

        for key in keys:
            cache.delete(key)

    def test_fetch(self):
        result = random.random()
        def get_fn(key):
            return result

        key = 'cache-test-fetch-' + str(random.random())
        cache.delete(key)

        fetched_result = cache.fetch(key, get_fn, None, None, 600)
        self.assertEqual(fetched_result, result)

        cache.delete(key)

if __name__ == '__main__':
    unittest.main()
