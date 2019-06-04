from __future__ import print_function
from __future__ import division

import pytest

from ..parsing import _get_aws_cred_id, _add_aws_creds


def test_get_aws_cred_id(client):
    cid = _get_aws_cred_id(client)
    assert cid == 0, "The wrong credential was returned!"
    client.credentials.list.assert_called_with(
        type="Amazon Web Services S3")


def test_get_aws_cred_id_no_cred(client):
    client.credentials.list.return_value = [{'owner': 'b', 'id': 1}]

    with pytest.raises(RuntimeError):
        _get_aws_cred_id(client)

    client.credentials.list.assert_called_with(
        type="Amazon Web Services S3")


@pytest.mark.parametrize(
    'params', [
        {},
        {'params': [{'p1': 10}], 'arguments': {'p1': 5}},
        {'aws_cred_id': 10}])
def test_add_aws_creds(params, client):
    if params and 'params' in params:
        res = {'params': [{'p1': 10}], 'arguments': {'p1': 5}}
    else:
        res = {'params': [], 'arguments': {}}
    res['params'].append({'name': 'AWS', 'type': 'credential_aws'})
    res['arguments'].update({'AWS': params.get('aws_cred_id', 0)})

    test_params = _add_aws_creds(params, client)
    assert test_params == res, (
        "AWS credential parameter not added properly!")
