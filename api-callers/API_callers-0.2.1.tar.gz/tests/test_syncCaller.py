from unittest import TestCase
from requests import Response
from API_callers.callers import SyncCaller


class TestSyncCaller(TestCase):
    def test_send_one(self):
        caller = SyncCaller({'fake': 'headers'},
                            {'payload': 'payloads'},
                            'https://jsonplaceholder.typicode.com/posts')
        response = caller.send()
        print(response)
        self.assertEqual(len(response), 1)
        self.assertIsInstance(response, list)
        self.assertIsInstance(response[0]['response'], Response)
        self.assertIn(type(response[0]['payload']), (dict, str))

    def test_send_3(self):
        payloads = [{'payload{}'.format(x): 'payloads'} for x in range(0, 3)]
        caller = SyncCaller({'fake': 'headers'},
                            payloads,
                            'https://jsonplaceholder.typicode.com/posts')
        response = caller.send()
        self.assertGreater(len(response), 1)
        self.assertIn('response', response[0].keys())
        self.assertIn('payload', response[0].keys())
        self.assertIsInstance(response, list)
        self.assertIsInstance(response[0]['response'], Response)
        self.assertIsInstance(response[1]['response'], Response)
        self.assertIsInstance(response[2]['response'], Response)

    def test_results(self):
        caller = SyncCaller({'fake': 'headers'},
                            {'payload': 'payloads'},
                            'https://jsonplaceholder.typicode.com/posts')
        self.assertEqual(len(caller.results), 1)
        self.assertIsInstance(caller.results, list)
        self.assertIsInstance(caller.results[0]['response'], Response)
