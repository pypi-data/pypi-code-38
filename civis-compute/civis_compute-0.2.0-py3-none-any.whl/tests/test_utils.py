from __future__ import print_function
from __future__ import division

from .conftest import mock

from ..utils import get_most_recent_run


@mock.patch('civiscompute.utils.civis.APIClient')
def test_get_most_recent_run(client_mock):
    client_mock.return_value.scripts.list_containers_runs.return_value = [
        {'finished_at': '2016-05-07', 'id': 0},
        {'finished_at': '2012-05-08', 'started_at': '2012-04-08', 'id': 1}]

    run_id = get_most_recent_run(-1)

    assert run_id == 0, "The most recent run was not returned!"
    client_mock.return_value.scripts.list_containers_runs.\
        assert_called_with(-1)


def test_get_most_recent_run_with_client():
    client_mock = mock.MagicMock()
    client_mock.scripts.list_containers_runs.return_value = [
        {'finished_at': '2010-05-07', 'id': 0},
        {'finished_at': '2012-01-08', 'started_at': '2012-04-08', 'id': 1}]

    run_id = get_most_recent_run(-1, client=client_mock)

    assert run_id == 1, "The most recent run was not returned!"
    client_mock.scripts.list_containers_runs.assert_called_with(-1)
