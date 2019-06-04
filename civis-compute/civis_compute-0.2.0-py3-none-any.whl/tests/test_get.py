from __future__ import print_function
from __future__ import division

import os
import pytest
import civis
from .conftest import mock

from ..get import _get


@pytest.mark.parametrize('runid', [None, 3])
@pytest.mark.parametrize('path', [None, 'pth'])
@pytest.mark.parametrize('no_output', [False, True])
@pytest.mark.parametrize('oname', ['civis_job_data_f', 'fff'])
@mock.patch('civiscompute.get.civis.io')
@mock.patch('civiscompute.get.open')
@mock.patch('civiscompute.get.civis.io.civis_to_file', autospec=True)
@mock.patch('civiscompute.get.get_most_recent_run', autospec=True)
@mock.patch('civiscompute.get.civis.APIClient')
def test_get(
        client_mock, gmr_mock, ctf_mock, open_mock, civisio_mock,
        runid, path, no_output, oname):
    """Test getting job outputs."""

    scriptid = 1
    outputs = [{'object_type': 'RANDOM', 'name': 'filename8', 'object_id': 8}]
    if not no_output:
        outputs.append(
            {'object_type': 'File', 'name': oname, 'object_id': 7})

    gmr_mock.return_value = runid or 2
    client_mock.return_value.scripts.list_containers_runs_outputs.\
        return_value = outputs
    open_mock.return_value.__enter__.return_value = 10

    _get(scriptid, runid=runid, path=path)

    # assert that the correct runid is used, if specified
    if runid is None:
        gmr_mock.assert_called_with(scriptid, client=client_mock.return_value)
    else:
        assert gmr_mock.call_count == 0

    # assert that the proper job run outputs are accessed
    client_mock.return_value.scripts.list_containers_runs_outputs.\
        assert_called_with(scriptid, runid or 2)

    # assert that if outputs are present and have the right name,
    # they are downloaded
    if not no_output and 'civis_job_data_' in oname:
        if path:
            oname = os.path.join(path, oname)
        open_mock.assert_called_with(oname, 'wb')
        civisio_mock.civis_to_file.assert_called_with(7, 10)
    else:
        assert open_mock.call_count == 0
        assert civisio_mock.civis_to_file.call_count == 0


@mock.patch('civiscompute.get.civis.APIClient')
def test_get_raises(client_mock):
    """Test errors squashed for get."""
    scriptids = [1]
    resp = mock.MagicMock()
    resp.content = None
    resp.reason = 'bad'
    resp.status_code = 502
    client_mock.return_value.scripts.list_containers_runs.side_effect \
        = civis.base.CivisAPIError(resp)

    with pytest.raises(SystemExit):
        _get(scriptids)
