from __future__ import print_function
from __future__ import division

import pytest
import click
import civis
from .conftest import mock

from ..stat import (
    _print_script_runs,
    _print_script_logs,
    _print_scripts,
    _parse_user_ids,
    _status)


@pytest.mark.parametrize('hidden', [True, False])
@pytest.mark.parametrize('state', [None, 'running'])
@pytest.mark.parametrize('user_ids', [[1], []])
@mock.patch('civiscompute.stat.civis.APIClient')
def test_print_scripts(client_mock, capsys, state, user_ids, hidden):
    scripts = [
        {'id': 0,
         'name': 'n0',
         'author': {'id': 1, 'username': 'a'},
         'state': 'running',
         'last_run': None,
         'created_at': None},
        {'id': 1,
         'name': 'n1',
         'author': {'id': 2, 'username': 'b'},
         'state': 'running',
         'last_run': {'startedAt': None, 'finishedAt': None},
         'created_at': 'now'},
        {'id': 2,
         'name': 'n2',
         'author': {'id': 1, 'username': 'a'},
         'state': 'canceled',
         'last_run': {'startedAt': '-1', 'finishedAt': None},
         'created_at': 'like-right-now'},
        {'id': 3,
         'name': 'n3',
         'author': {'id': 2, 'username': 'b'},
         'state': 'canceled',
         'last_run': {'startedAt': '-2', 'finishedAt': '-3'},
         'created_at': 'yesterday'}]

    hidden_scripts = [
        {'id': 4,
         'name': 'n4',
         'author': {'id': 1, 'username': 'a'},
         'state': 'running',
         'last_run': {'startedAt': None, 'finishedAt': '-4'},
         'created_at': 'last-week'},
        {'id': 5,
         'name': 'n5',
         'author': {'id': 2, 'username': 'b'},
         'state': 'running',
         'last_run': {'startedAt': '-6', 'finishedAt': '-5'},
         'created_at': 'last-decade'},
        {'id': 6,
         'name': 'n6',
         'author': {'id': 1, 'username': 'a'},
         'state': 'canceled',
         'last_run': {'startedAt': '-8', 'finishedAt': '-7'},
         'created_at': 'sometime-in-the-last-day'},
        {'id': 7,
         'name': 'n7',
         'author': {'id': 2, 'username': 'b'},
         'state': 'canceled',
         'last_run': {'startedAt': '-10', 'finishedAt': '-9'},
         'created_at': 'yep-it-was'}]

    def _get_scripts(*args, **kwargs):
        if kwargs.get('hidden', False):
            _scripts = hidden_scripts
        else:
            _scripts = scripts

        if 'status' in kwargs and kwargs['status']:
            _scripts = [s for s in _scripts if s['state'] == kwargs['status']]
        if 'author' in kwargs and kwargs['author']:
            auths = [int(v) for v in kwargs['author'].strip().split(',')]
            _scripts = [s for s in _scripts if s['author']['id'] in auths]
        return _scripts

    client_mock.return_value.scripts.list = _get_scripts

    _print_scripts(user_ids, state, hidden)

    client_mock.assert_called_with(resources='all')

    out, err = capsys.readouterr()
    lines = out.split('\n')
    head = ("id                   author               status               "
            "created                   started                   finished"
            "                  name")
    assert lines[0].strip() == head, "Header for listing scripts is wrong!"

    all_scripts = scripts
    if hidden:
        all_scripts += hidden_scripts
    if state:
        all_scripts = [s for s in all_scripts if s['state'] == 'running']
    if user_ids:
        all_scripts = [s for s in all_scripts if s['author']['id'] == 1]

    for i, s in enumerate(all_scripts):
        items = lines[i+1].strip().split()
        assert items[0] == str(s['id']), (
            "Script id is wrong!")
        assert items[1] == s['author']['username'], (
            "Script username is wrong!")
        assert items[2] == s['state'], (
            "Script state is wrong!")
        assert items[3] == s['created_at'] or '-', (
            "Script created time is wrong!")
        if s['last_run']:
            assert items[4] == s['last_run']['startedAt'] or '-', (
                "Script started time is wrong!")
            assert items[5] == s['last_run']['finishedAt'] or '-', (
                "Script finished time is wrong!")
        else:
            assert items[4] == '-', (
                "Script started time is wrong!")
            assert items[5] == '-', (
                "Script finished time is wrong!")
        assert items[6] == s['name'], (
            "Script name is wrong!")


@pytest.mark.parametrize('runid', [2, None])
@mock.patch('civiscompute.stat.get_most_recent_run', autospec=True)
@mock.patch('civiscompute.stat.civis.APIClient')
def test_print_script_logs(client_mock, gmr_mock, capsys, runid):
    log_data = {
        'name': 'cool',
        'docker_command': 'echo 1 && \\\n  echo 2',
        'id': 4,
        'rand': 10}
    client_mock.return_value.scripts.get_containers.return_value = log_data
    gmr_mock.return_value = 5
    logs = [
        {'created_at': '3', 'message': 'c'},
        {'created_at': '2', 'message': 'b'},
        {'created_at': '1', 'message': 'a'}]
    client_mock.return_value.scripts.list_containers_runs_logs.return_value \
        = logs

    _print_script_logs(-1, runid=runid)

    client_mock.return_value.scripts.get_containers.assert_called_with(-1)
    if runid is None:
        assert gmr_mock.call_count == 1
    client_mock.return_value.scripts.list_containers_runs_logs.\
        assert_called_with(-1, runid or 5)

    out, err = capsys.readouterr()
    lines = out.split('\n')[:-1]  # remove extra blank line
    assert lines[0] == 'name: cool', "Script name is wrong!"
    assert lines[1] == 'id: 4', "Script ID is wrong!"
    assert lines[2] == 'docker_command:', (
        "Docker command head is wrong!")
    assert lines[3] == '  echo 1 && \\', (
        "First line of docker command is not right!")
    assert lines[4] == '    echo 2', (
        "Second line of docker command is not right!")
    assert lines[5] == 'rand: 10', (
        "Reamining key not printed!")
    assert lines[6] == 'log file:', (
        "Log file head was not printed!")
    assert lines[7] == '  [1] a', (
        "Log file line 1 was not printed!")
    assert lines[8] == '  [2] b', (
        "Log file line 2 was not printed!")
    assert lines[9] == '  [3] c', (
        "Log file line 3 was not printed!")
    assert len(lines) == 10, "Too many lines were printed!"


@mock.patch('civiscompute.stat.get_most_recent_run', autospec=True)
@mock.patch('civiscompute.stat.civis.APIClient')
def test_print_script_logs_no_runs(client_mock, gmr_mock, capsys):
    log_data = {
        'name': 'cool',
        'docker_command': 'echo 1 && \\\n  echo 2',
        'id': 4,
        'rand': 10}
    client_mock.return_value.scripts.get_containers.return_value = log_data
    gmr_mock.return_value = None
    logs = [
        {'created_at': '3', 'message': 'c'},
        {'created_at': '2', 'message': 'b'},
        {'created_at': '1', 'message': 'z'}]
    client_mock.return_value.scripts.list_containers_runs_logs.return_value \
        = logs

    _print_script_logs(-1)

    client_mock.return_value.scripts.get_containers.assert_called_with(-1)
    assert gmr_mock.call_count == 1
    assert client_mock.return_value.scripts.list_containers_runs_logs.\
        call_count == 0

    out, err = capsys.readouterr()
    lines = out.split('\n')[:-1]  # remove extra blank line
    assert lines[0] == 'name: cool', "Script name is wrong!"
    assert lines[1] == 'id: 4', "Script ID is wrong!"
    assert lines[2] == 'docker_command:', (
        "Docker command head is wrong!")
    assert lines[3] == '  echo 1 && \\', (
        "First line of docker command is not right!")
    assert lines[4] == '    echo 2', (
        "Second line of docker command is not right!")
    assert lines[5] == 'rand: 10', (
        "Reamining key not printed!")
    assert lines[6] == 'log file: -', (
        "Log file head was not printed!")
    assert len(lines) == 7, "Too many lines were printed!"


@mock.patch('civiscompute.stat.get_most_recent_run', autospec=True)
@mock.patch('civiscompute.stat.civis.APIClient')
def test_print_script_logs_raises(client_mock, gmr_mock):
    resp = mock.MagicMock()
    resp.content = None
    resp.reason = 'bad'
    resp.status_code = 502

    client_mock.return_value.scripts.get_containers.side_effect \
        = civis.base.CivisAPIError(resp)
    gmr_mock.return_value = 5

    with pytest.raises(SystemExit):
        _print_script_logs(-1)


@mock.patch('civiscompute.stat.civis.APIClient')
def test_print_script_runs(client_mock, capsys):
    run_data = [
        {'finished_at': '2016-05-07',
         'started_at': '2012-04-08',
         'id': 0,
         'state': 'happy',
         'error': None},
        {'finished_at': '2012-05-08',
         'started_at': '2012-04-02',
         'id': 1,
         'state': 'sad',
         'error': 'bad'}]
    client_mock.return_value.scripts.list_containers_runs.return_value \
        = run_data

    _print_script_runs(-1)

    client_mock.return_value.scripts.list_containers_runs.\
        assert_called_with(-1)

    out, err = capsys.readouterr()
    lines = out.split('\n')
    head = ("run id                    started                   finished"
            "                  status                    error msg")
    assert lines[0].strip() == head, "Run listing header is wrong!"

    for i in range(2):
        items = lines[i+1].strip().split()
        assert items[0] == str(run_data[i]['id']), (
            "run id is wrong for runs listing!")
        assert items[1] == run_data[i]['started_at'], (
            "starting time is wrong for runs listing!")
        assert items[2] == run_data[i]['finished_at'], (
            "finishing time is wrong for runs listing!")
        assert items[3] == run_data[i]['state'], (
            "state is wrong for runs listing!")
        err = run_data[i]['error'] or '-'
        assert ' '.join(items[4:]) == err, (
            "error is wrong for runs listing!")


@mock.patch('civiscompute.stat.civis.APIClient')
def test_print_script_runs_raises(client_mock, capsys):
    resp = mock.MagicMock()
    resp.content = None
    resp.reason = 'bad'
    resp.status_code = 502
    client_mock.return_value.scripts.list_containers_runs.side_effect \
        = civis.base.CivisAPIError(resp)

    with pytest.raises(SystemExit):
        _print_script_runs(-1)


@pytest.mark.parametrize('users', ['', 'me,you,everyone'])
def test_parse_user_ids(users):
    cv_mock = mock.MagicMock()
    cv_mock.users.list.side_effect = [[{'id': 1}], [{'id': 2}], [{'id': 3}]]

    ids = _parse_user_ids(users, cv_mock)

    if users:
        assert ids == [1, 2, 3], "The returned IDs are wrong!"
        cv_mock.users.list.assert_has_calls([
            mock.call(query='me'),
            mock.call(query='you'),
            mock.call(query='everyone')])
    else:
        assert ids == [], "The returned IDs are wrong!"
        assert cv_mock.call_count == 0


def test_status_raises():
    with pytest.raises(click.UsageError) as e:
        _status(-1, False, None, True, 10, False, False, 'all')

    assert '`--runs` or `--run-id`' in str(e.value), (
        "The wrong usage error was raised for runs and run IDs!")

    with pytest.raises(click.UsageError) as e:
        _status(-1, False, None, False, None, True, False, 'all')

    assert '`--last` or `scriptid`' in str(e.value), (
        "The wrong usage error was raised for script IDs and last!")


@pytest.mark.parametrize('mine', [True, False])
@pytest.mark.parametrize('user', [None, 'me,you'])
@pytest.mark.parametrize('hidden', [True, False])
@pytest.mark.parametrize('state', ['all', 'running'])
@mock.patch('civiscompute.stat._print_scripts', autospec=True)
@mock.patch('civiscompute.stat.civis')
def test_status_scripts(cv_mock, ps_mock, mine, user, hidden, state):
    cv_mock.APIClient.return_value.users.list_me.return_value = {'id': 1}
    cv_mock.APIClient.return_value.users.list.side_effect \
        = [[{'id': 2}], [{'id': 3}]]

    _status(None, mine, user, False, None, False, hidden, state)

    user_ids = []
    if mine:
        user_ids.append(1)

    if user:
        user_ids.extend([2, 3])

    if state != 'all':
        _state = state
    else:
        _state = None

    ps_mock.assert_called_with(
        user_ids,
        _state,
        hidden)

    if mine:
        assert cv_mock.APIClient.return_value.users.list_me.call_count == 1
    else:
        assert cv_mock.APIClient.return_value.users.list_me.call_count == 0


@mock.patch('civiscompute.stat._print_script_runs', autospec=True)
@mock.patch('civiscompute.stat.civis')
def test_status_script_runs(cv_mock, ps_mock):
    _status(-10, False, None, True, None, False, False, 'all')

    ps_mock.assert_called_with(-10)


@pytest.mark.parametrize('runid', [-11, None])
@mock.patch('civiscompute.stat._print_script_logs', autospec=True)
@mock.patch('civiscompute.stat.civis')
def test_status_script_logs(cv_mock, ps_mock, runid):
    _status(-10, False, None, False, runid, False, False, 'all')

    ps_mock.assert_called_with(-10, runid=runid)


@mock.patch('civiscompute.stat.LASTSCRIPTID_LOC', 'lastscript')
@mock.patch('civiscompute.stat._print_script_runs', autospec=True)
@mock.patch('civiscompute.stat.civis')
def test_status_last(cv_mock, ps_mock, cleandir):

    with open('lastscript', 'w') as fp:
        fp.write('-10')

    _status(None, False, None, True, None, True, False, 'all')

    ps_mock.assert_called_with(-10)


@mock.patch('civiscompute.stat.LASTSCRIPTID_LOC', 'lastscript')
@mock.patch('civiscompute.stat._print_script_runs', autospec=True)
@mock.patch('civiscompute.stat.civis')
def test_status_last_raises(cv_mock, ps_mock, cleandir):
    with pytest.raises(SystemExit):
        _status(None, False, None, True, None, True, False, 'all')
