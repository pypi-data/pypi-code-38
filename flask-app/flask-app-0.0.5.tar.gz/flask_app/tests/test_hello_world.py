from tests.base_test import BaseTestCase


class TestHelloWorld(BaseTestCase):

    def test_hello_world_succeeds(self):
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'message': 'Hello'})
