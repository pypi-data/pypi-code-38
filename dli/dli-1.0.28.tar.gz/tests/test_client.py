import unittest
import mock
from requests import Session

from dli.client import dli_client


class TestAuth(unittest.TestCase):

    @mock.patch.object(Session, 'post')
    def test_handle_auth_error(self, post):
        text = 'Some server error message'
        post.return_value = mock.Mock(status_code=401, text=text)
        with self.assertRaises(dli_client.AuthenticationFailure) as cm:
            dli_client._get_auth_key('api-key', 'api-root')

        self.assertEqual(str(cm.exception), text)

    @mock.patch.object(Session, 'post')
    def test_handle_auth_error_for_403_response(self, post):
        """
        Should show a generic response message
        """
        post.return_value = mock.Mock(status_code=403)
        with self.assertRaises(dli_client.AuthenticationFailure) as cm:
            dli_client._get_auth_key('api-key', 'api-root')
            
        exception_message = str(cm.exception)
        self.assertIn(dli_client.AuthenticationFailure.GENERIC_ERROR_MESSAGE, exception_message)
        self.assertIn('api-root', exception_message)

    @mock.patch.object(Session, 'post')
    def test_auth_error_for_unknown_auth_error(self, post):
        """
        Should show a generic response message if no error message
        """
        post.return_value = mock.Mock(status_code=401, text='')

        with self.assertRaises(dli_client.AuthenticationFailure) as cm:
            dli_client._get_auth_key('api-key', 'api-root')

        self.assertEqual(
            str(cm.exception),
            dli_client.AuthenticationFailure.GENERIC_ERROR_MESSAGE
        )