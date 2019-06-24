from unittest.mock import patch

import pytest

from algernon.aws import Bullhorn


@pytest.mark.bullhorn
class TestBullhorn:
    def test_bullhorn_retrieve(self):
        bullhorn = Bullhorn.retrieve(profile='dev')
        assert bullhorn

    def test_bullhorn_live_send(self):
        bullhorn = Bullhorn.retrieve(profile='dev')
        arn = 'arn:aws:sns:us-east-1:726075243133:test'
        bullhorn.publish('test', arn, f'hello world, {1}')

    def test_bullhorn_batch_live_send(self):
        bullhorn = Bullhorn.retrieve(profile='dev')
        arn = 'arn:aws:sns:us-east-1:726075243133:test'
        with bullhorn as batch:
            for _ in range(100):
                batch.publish('test', arn, f'hello world, {_}')

    def test_bullhorn_batch_send(self):
        with patch('botocore.client.BaseClient._make_api_call') as mock:
            bullhorn = Bullhorn({'test': 'test_arn'})
            with bullhorn as batch:
                for _ in range(100):
                    batch.publish('test', 'some_arn', f'hello world, {_}')
            assert mock.called
            assert mock.call_count == 100
