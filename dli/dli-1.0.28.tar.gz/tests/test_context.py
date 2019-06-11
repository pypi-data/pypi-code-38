import unittest
from dli.client.context import Context


class ContextTestCase(unittest.TestCase):

    valid_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImlhdCI6MTUxMzMzMTUwOSwiZXhwIjo5NTEzMzM1MTA5fQ.e30.fjav6VOdXAnE6WgUwSxEbrNuiqQBSEalOd177F9UrCM"
    expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImlhdCI6MTUxMzMzMTUwOSwiZXhwIjoxNTEzMzM1MTA5fQ.e30.-vTTDvptpjPrG2PO1GBo1OOlBqvx6D_gPGnU7Tw-YII"

    def test_can_decode_valid_jwt_token(self):
        ctx = Context(
            "key",
            "root",
            None,
            self.valid_token
        )
        self.assertFalse(ctx.session_expired)

    def test_can_detect_token_is_expired(self):
        ctx = Context(
            "key",
            "root",
            None,
            self.expired_token
        )
        self.assertTrue(ctx.session_expired)

    def test_when_token_cant_be_decoded_then_we_assume_no_session_expiration(self):
        ctx = Context(
            "key",
            "root",
            None,
            "invalid.token"
        )
        self.assertFalse(ctx.session_expired)