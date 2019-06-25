from base_test import BaseTestCase


class TestHelloWorld(BaseTestCase):

    def test_hello_world_succeds(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'msg': 'Hello'})