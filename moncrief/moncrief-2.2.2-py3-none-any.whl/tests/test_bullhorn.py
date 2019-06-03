import boto3
import pytest

from algernon.aws import Bullhorn


@pytest.mark.bullhorn
class TestBullhorn:
    def test_bullhorn_retrieve(self):
        bullhorn = Bullhorn.retrieve(profile='dev')
        assert bullhorn
