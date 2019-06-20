import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from flywheel_common import errors

class ErrorsTestCases(unittest.TestCase):

    def test_formatting(self):
        err = errors.ResourceError('/resource/path')
        self.assertEqual(str(err), 'Resource error on "/resource/path"')

        err = errors.ResourceNotFound('/resource/path')
        self.assertEqual(str(err), 'Could not find resource "/resource/path"')

        err = errors.RemoteConnectionError(exc=err)
        self.assertEqual(str(err), 'Remote connection error, Could not find resource "/resource/path"')

        err = errors.RemoteConnectionError()
        self.assertEqual(str(err), 'Remote connection error, ')

        err = errors.PermissionError('/resource/path')
        self.assertEqual(str(err), 'Insufficient permissions for "/resource/path"')

        err = errors.HTTPStatusError(404, 'Not Found')
        self.assertEqual(str(err), '404 Not Found\n  detail: None')

        err = errors.HTTPStatusError(404, 'Not Found', 'No such thing!')
        self.assertEqual(str(err), '404 Not Found\n  detail: No such thing!')

    def test_custom_message(self):
        err = errors.ResourceNotFound('/my/path', msg='No such thing as a {path}')
        self.assertEqual(str(err), 'No such thing as a /my/path')

    def test_raise_for_http_status(self):
        errors.HTTPStatusError.raise_for_status(None)  # Should not raise

        resp = mock.MagicMock()
        resp.status_code = 200
        resp.ok = True

        errors.HTTPStatusError.raise_for_status(resp)  # Should not raise

        resp.ok = False
        resp.status_code = 403
        resp.reason = 'Forbidden'
        resp.json.return_value = {'message': 'That is not allowed!'}

        try:
            errors.HTTPStatusError.raise_for_status(resp)
            self.fail('Expected HTTPStatusError!')
        except errors.HTTPStatusError as err:
            assert err.status_code == 403
            assert err.reason == 'Forbidden'
            assert err.detail == 'That is not allowed!'
