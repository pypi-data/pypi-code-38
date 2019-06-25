from unittest import TestCase
from restclients_core.models import MockHTTP
from uw_bridge import Bridge_DAO
from uw_bridge.tests import fdao_bridge_override


@fdao_bridge_override
class TestBridgeDao(TestCase):

    def test_is_using_file_dao(self):
        self.assertTrue(Bridge_DAO().is_mock())

    def test_custom_headers(self):
        self.assertEqual(Bridge_DAO()._custom_headers('GET', '/', {}, None),
                         {'Authorization': 'Basic MDAwMDA6MDAwMDA='})

    def test_edit_mock_response(self):
        response = MockHTTP()
        response.status = 404
        Bridge_DAO()._edit_mock_response('DELETE', '/api/admin/users/195',
                                         {}, None, response)
        self.assertEqual(response.status, 204)
