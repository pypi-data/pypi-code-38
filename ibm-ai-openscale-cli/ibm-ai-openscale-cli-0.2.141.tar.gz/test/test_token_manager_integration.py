# coding=utf-8

import os
import pytest
from ibm_ai_openscale_cli.setup_classes.token_manager import TokenManager
from unittest import TestCase


@pytest.mark.skipif(
    os.getenv('APIKEY') is None, reason='requires APIKEY')
class TokenManagerTests(TestCase):
    def test_get_iam_token(self):
        token_manager = TokenManager(apikey=os.environ['APIKEY'])
        access_token = token_manager.get_token()
        assert access_token is not None

    def test_get_uaa_token(self):
        token_manager = TokenManager(
            apikey=os.environ['APIKEY'], iam_token=False)
        access_token = token_manager.get_token()
        assert access_token is not None
