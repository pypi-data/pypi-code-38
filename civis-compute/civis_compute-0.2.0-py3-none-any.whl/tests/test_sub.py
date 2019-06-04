from __future__ import print_function
from __future__ import division

import os
import pytest
import civis
from .conftest import mock

from ..sub import (
    _upload_files,
    _build_container_cmd,
    _print_job,
    _post_and_run_job,
    _record_last_jobid,
    _sub_job,
    _sub)


@pytest.mark.parametrize('use_cache', [True, False])
@mock.patch('civiscompute.sub.civis.io.file_to_civis', autospec=True)
@mock.patch('civiscompute.sub.FileIDCache', autospec=True)
def test_upload_files(cache_mock, cv_mock, use_cache, cleandir):
    with open('a.txt', 'w') as fp:
        fp.write('a')

    with open('b.txt', 'w') as fp:
        fp.write('b')

    fnames = ['a.txt', 'b.txt']
    cache_mock.return_value.get_fileid.side_effect = [-1, -2]
    cv_mock.side_effect = [-3, -4]

    fileids = _upload_files(fnames, use_cache)

    if use_cache:
        assert fileids == {'a.txt': '-1', 'b.txt': '-2'}, (
            "fileids are wrong!")
        assert cache_mock.return_value.get_fileid.call_count == 2, (
            "FileIDCache not called!")
        assert cv_mock.call_count == 0, "file_to_civis called!"
    else:
        assert fileids == {'a.txt': '-3', 'b.txt': '-4'}, (
            "fileids are wrong!")
        assert cache_mock.return_value.get_fileid.call_count == 0, (
            "FileIDCache called!")
        assert cv_mock.call_count == 2, "file_to_civis not called!"


@mock.patch('civiscompute.sub.LASTSCRIPTID_LOC', 'a/lastid')
def test_record_last_jobid(cleandir):
    _record_last_jobid(-1)

    with open('a/lastid', 'r') as fp:
        data = fp.read()
    assert data.strip() == '-1', "Last job ID not written properly!"


@mock.patch('civiscompute.sub.LASTSCRIPTID_LOC', 'a/lastid')
@mock.patch('civiscompute.sub.open')
def test_record_last_jobid_squash(open_mock, cleandir):
    open_mock.side_effect = OSError("Bad thing!")
    _record_last_jobid(-1)
    assert not os.path.exists('a/lastid'), "Last job ID should not exist!"


def test_post_and_run_job():
    cv_mock = mock.MagicMock()
    cv_mock.scripts.post_containers.return_value = {'id': -1}
    req = -10
    container_cmd = -11
    docker_image = -12
    params = {'a': -13}

    retid = _post_and_run_job(
        req, container_cmd, docker_image, params, cv_mock)

    cv_mock.scripts.post_containers.assert_called_with(
        req, container_cmd, docker_image, **params)
    cv_mock.scripts.post_containers_runs.assert_called_with(-1)
    assert retid == -1, "Wrong job ID returned!"


@pytest.mark.parametrize('fail_post', [True, False])
def test_post_and_run_job_raises(fail_post, capsys):
    cv_mock = mock.MagicMock()
    resp = mock.MagicMock()
    resp.content = None
    resp.reason = 'bad stuff'
    resp.status_code = 5018
    if fail_post:
        cv_mock.scripts.post_containers.side_effect \
            = civis.base.CivisAPIError(resp)
    else:
        cv_mock.scripts.post_containers.return_value = {'id': -1}
        cv_mock.scripts.post_containers_runs.side_effect \
            = civis.base.CivisAPIError(resp)
    req = -10
    container_cmd = -11
    docker_image = -12
    params = {'a': -13}

    with pytest.raises(SystemExit):
        _post_and_run_job(req, container_cmd, docker_image, params, cv_mock)

    cv_mock.scripts.post_containers.assert_called_with(
        req, container_cmd, docker_image, **params)

    _, err = capsys.readouterr()
    if fail_post:
        assert cv_mock.scripts.post_containers_runs.call_count == 0
        assert "Could not create container" in err, (
            "Stderr is not right for failed create!")
    else:
        cv_mock.scripts.post_containers_runs.assert_called_with(-1)
        assert "Could not run container -1" in err, (
            "Stderr is not right for failed run!")


def test_print_job(capsys):
    req = {'cpu': 10, 'memory': 11, 'disk_space': 12}
    container_cmd = 'blah && \\\nblah && \\\nblah'
    docker_image = 'containers!'
    params = {'a': 13}

    _print_job(req, container_cmd, docker_image, params)

    out, err = capsys.readouterr()
    assert err == '', "Stderr was produced!"

    test_out = """\
container script config:
  a: 13
  docker_image_name: containers!
  required_resources:
    cpu: 10
    disk_space: 12
    memory: 11
container script cmd:
  blah && \\
  blah && \\
  blah
"""
    assert out == test_out, "Stdout is wrong!"


@pytest.mark.parametrize('stype', ['py', 'ipynb', 'R', 'r', 'b', 'sh', None])
@pytest.mark.parametrize('cli_args', [('a', 'b'), tuple()])
@pytest.mark.parametrize('fileids', [{}, {'a/f1': -1, 'b/f2': -2, 'a/f3': -3}])
@pytest.mark.parametrize('repo_cmd', [None, 'pip me'])
@pytest.mark.parametrize('shell_cmd', [None, 'sh me'])
def test_build_container_cmd(
        stype, cli_args, fileids, repo_cmd, shell_cmd, cleandir):

    if stype:
        script = 's' + '.' + stype
        with open(script, 'w') as fp:
            fp.write('blah')

        if stype == 'py':
            remote_script = 'rs.py'
        else:
            remote_script = script
    else:
        script = 's'
        remote_script = script

    cmd = _build_container_cmd(
        script, remote_script, cli_args, fileids, repo_cmd, shell_cmd)

    lines = cmd.split('\n')

    if cli_args:
        arg_str = ' a b '
    else:
        arg_str = ' '
    if stype == 'py':
        cmd = 'python '
    elif stype == 'r' or stype == 'R':
        cmd = ('Rscript --default-packages=methods,'
               'datasets,utils,grDevices,graphics,stats ')
    elif stype == 'ipynb':
        cmd = "ipython --InteractiveShell.colors='nocolor' "
    elif stype:
        cmd = 'sh '
    else:
        cmd = ''
    run_str = '%s%s%s&& \\' % (cmd, remote_script, arg_str)
    assert run_str in lines

    if stype:
        assert 'chmod a+rwx %s && \\' % remote_script in lines

    if repo_cmd:
        assert 'cd /app && %s && cd .. && \\' % repo_cmd in lines
        # repo command comes before run
        assert (
            lines.index('cd /app && %s && cd .. && \\' % repo_cmd) <
            lines.index(run_str))

    if shell_cmd:
        assert '%s && \\' % shell_cmd in lines

    # shell command comes before the repo command
    if shell_cmd and repo_cmd:
        assert (
            lines.index('%s && \\' % shell_cmd) <
            lines.index('cd /app && %s && cd .. && \\' % repo_cmd))

    if fileids:
        assert 'mkdir -p a && \\' in lines
        assert 'mkdir -p b && \\' in lines
        assert 'civis files download -1 a/f1 && \\' in lines
        assert 'civis files download -2 b/f2 && \\' in lines
        assert 'civis files download -3 a/f3 && \\' in lines

        # have to make dirs before we download
        assert (
            lines.index('mkdir -p a && \\') <
            lines.index('civis files download -1 a/f1 && \\'))
        assert (
            lines.index('mkdir -p b && \\') <
            lines.index('civis files download -2 b/f2 && \\'))
        assert (
            lines.index('mkdir -p a && \\') <
            lines.index('civis files download -3 a/f3 && \\'))

        # all files should come before any shell or repo
        if shell_cmd:
            assert (
                lines.index('civis files download -3 a/f3 && \\') <
                lines.index('%s && \\' % shell_cmd))

        if repo_cmd:
            assert (
                lines.index('civis files download -3 a/f3 && \\') <
                lines.index('cd /app && %s && cd .. && \\' % repo_cmd))


@pytest.mark.parametrize('script', ['script.ipynb', 'script.py'])
@mock.patch('civiscompute.sub.TemporaryDirectory', autospec=True)
@mock.patch('civiscompute.sub.civis.APIClient', autospec=True)
@mock.patch('civiscompute.sub._record_last_jobid', autospec=True)
@mock.patch('civiscompute.sub._sub_job', autospec=True)
def test_sub(mock_sub, mock_rcd, mock_cv, mock_tmp,
             script, cleandir, example_notebook):
    cli_args = ['1', '2']
    dry_run = False
    cli_params = {'a': 5, 'dry_run': dry_run}
    mock_sub.return_value = 5
    mock_tmp.return_value.__enter__.return_value = 'tmp'
    os.makedirs('tmp')

    with open(script, 'w') as fp:
        if script.endswith('.ipynb'):
            fp.write(example_notebook)
        else:
            fp.write('test')

    _sub(script, cli_args, cli_params)

    if script.endswith('.ipynb'):
        mock_sub.assert_called_with(
            os.path.join('tmp', script),
            script,
            cli_args,
            cli_params,
            mock_cv.return_value,
            dry_run)
    else:
        mock_sub.assert_called_with(
            script,
            script,
            cli_args,
            cli_params,
            mock_cv.return_value,
            dry_run)
    mock_rcd.assert_called_with(5)


@pytest.mark.parametrize('repo', [None, 'gitrepo'])
@pytest.mark.parametrize('dry_run', [True, False])
@pytest.mark.parametrize('script', ['script.r', 'script.py', 'echo 1'])
@mock.patch('civiscompute.sub.civis.io.file_to_civis', autospec=True)
@mock.patch('civiscompute.sub._post_and_run_job', autospec=True)
def test_sub_job(mock_sub, mock_ftc, script, dry_run, repo, cleandir):

    if script.endswith('.r') or script.endswith('.py'):
        with open(script, 'w') as fp:
            fp.write('#CIVIS files=test.txt\n')
            fp.write('#CIVIS name=my script\n')

        with open('test.txt', 'w') as fp:
            fp.write('hi!\n')

    with open('test2.txt', 'w') as fp:
        fp.write('hi again!')

    cli_args = ('a', 'b', 'test2.txt')
    cli_params = {
        'required_resources': {'cpu': 567},
        'shell_cmd': 'what'}
    if repo:
        cli_params['repo_http_uri'] = repo
    client = mock.MagicMock()
    mock_sub.return_value = 5
    mock_ftc.side_effect = [6, 7, 8]

    if script.endswith('.r'):
        remote_script = 'blah.r'
    else:
        remote_script = script

    jobid = _sub_job(
        script, remote_script, cli_args, cli_params, client, dry_run)

    if dry_run:
        # make sure no jobs are submitted
        assert jobid is None
        assert mock_sub.call_count == 0
    else:
        # make sure job is submitted only once
        assert jobid == 5
        assert mock_sub.call_count == 1

        # check arguments for job submission
        args, _ = mock_sub.call_args

        # resources
        assert args[0] == {'cpu': 567, 'memory': 8192, 'disk_space': 16.0}

        # docker image name
        if script.endswith('.r'):
            assert args[2] == 'civisanalytics/datascience-r'
        elif script.endswith('.py'):
            assert args[2] == 'civisanalytics/datascience-python'

        # parameters
        test_params = {}
        if script.endswith('.r') or script.endswith('.py'):
            test_params['name'] = 'my script'
        if repo:
            test_params['repo_http_uri'] = repo
        assert args[3] == test_params

        # make sure repo_cmd and repo_http_uri were processed correctly
        if repo and script.endswith('.py'):
            assert 'python setup.py install' in args[1]

        # did the shell_cmd get through?
        assert 'what &&' in args[1]

        # make sure files are downloaded into the container
        if script.endswith('.r') or script.endswith('.py'):
            assert 'civis files download 6' in args[1]
            assert 'civis files download 7' in args[1]
            assert 'civis files download 8' in args[1]
        else:
            assert 'civis files download 6' in args[1]

        # check command invocation
        if script.endswith('.r'):
            assert ('Rscript --default-packages=methods,datasets,utils,'
                    'grDevices,graphics,stats blah.r '
                    'a b test2.txt') in args[1]
        elif script.endswith('.py'):
            assert 'python script.py a b test2.txt' in args[1]
        else:
            assert script + ' a b test2.txt' in args[1]

    # make sure files are uploaded properly
    if dry_run:
        assert mock_ftc.call_count == 0
    elif script.endswith('.r') or script.endswith('.py'):
        assert mock_ftc.call_count == 3
    else:
        assert mock_ftc.call_count == 1
