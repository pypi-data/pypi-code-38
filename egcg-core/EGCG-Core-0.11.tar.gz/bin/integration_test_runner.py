#!/usr/bin/env python
import os
import sys
import shutil
import random
import pytest
import argparse
from io import StringIO
from string import hexdigits
from subprocess import check_call, check_output, CalledProcessError
from contextlib import redirect_stdout
from egcg_core import notifications, integration_testing


def resolve_path(fp):
    if fp and not os.path.isabs(fp):
        return os.path.join(os.getcwd(), fp)
    return fp


def random_string(strlen=6):
    s = ''
    for i in range(strlen):
        s += random.choice(hexdigits)
    return s


def main():
    a = argparse.ArgumentParser()
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument('--local', help='Use a copy of a local directory for testing - must be an absolute path')
    g.add_argument('--remote', help='Use a checked out Git repo for testing')
    a.add_argument('--branch', help='Checkout a branch in the working dir')
    a.add_argument('--integration_cfg', help='Absolute path to an integration test config file')
    a.add_argument('--integration_test_target', default='integration_tests', help='Subdir in the working dir containing the integration tests')
    a.add_argument('--app_config')
    a.add_argument('--app_config_env_var')
    a.add_argument('--coverage_targets', nargs='+', help='Submodules to pass to pytest-cov for coverage metrics')
    a.add_argument('--stdout', action='store_true', help='Write test results to stdout')
    a.add_argument('--email', action='store_true', help='Email test results')
    a.add_argument('--log_repo', help='Log test results to a timestamped file in log_repo')
    a.add_argument('--test', nargs='+', default=[], help='Whitelist of integration tests to run. Run everything if not specified')
    a.add_argument('--ls', action='store_true', help='List all available integration tests')
    a.add_argument('--nocleanup', dest='cleanup', action='store_false', help='Don\'t clean up working dir afterwards')
    a.add_argument('-n', help='Number of concurrent processes to run tests in')
    args = a.parse_args()

    top_level = os.getcwd()

    app_config_master_copy = resolve_path(args.app_config)
    if args.integration_cfg:
        os.environ['INTEGRATIONCONFIG'] = args.integration_cfg

    run_dir = os.path.join(top_level, 'integration_test_%s' % random_string())
    os.mkdir(run_dir)
    os.chdir(run_dir)

    if args.local:
        assert os.path.isabs(args.local)
        checked_out_project = os.path.basename(args.local)
        assert os.path.isabs(args.local), 'Need an absolute path for local dirs'
        check_call(['cp', '-r', args.local, checked_out_project])  # shutil copytree fails for some reason
    else:
        assert args.remote
        check_call(['git', 'clone', args.remote])
        checked_out_project = os.path.basename(args.remote).split('.')[0]

    assert os.path.isdir(checked_out_project)
    os.chdir(checked_out_project)

    if args.branch:
        check_call(['git', 'checkout', args.branch])

    if app_config_master_copy:
        app_config = os.path.join(os.getcwd(), 'app_config.yaml')
        shutil.copy(app_config_master_copy, app_config)
        if args.app_config_env_var:
            os.environ[args.app_config_env_var] = app_config

    sys.path.append(os.getcwd())
    pytest_args = [args.integration_test_target, '--tb=short']

    if args.ls:
        pytest_args.append('--collect-only')
    else:
        if args.test:
            pytest_args.extend(['-k', ' or '.join(args.test)])

        if args.coverage_targets:
            pytest_args.append('--cov')
            pytest_args.extend(args.coverage_targets)
            pytest_args.extend(['--cov-report', 'term-missing'])

        if args.n:
            pytest_args.extend(['-n', args.n])

    checks_log = 'checks.log'
    start_time = integration_testing.now()
    with open(checks_log, 'w') as f:
        f.write('test_method\tcheck_name\tassert_method\tresult\targs\n')

    s = StringIO()
    with redirect_stdout(s):
        exit_status = pytest.main(pytest_args)
    end_time = integration_testing.now()

    try:
        git_commit = check_output(['git', 'log', '--format=Run on commit %h%d, made on %aD', '-1']).decode()
    except CalledProcessError:
        git_commit = 'Git info not available'

    test_output = '------\nIntegration test finished\n%s\nStart time: %s, finish time: %s\nPytest output:\n' % (
        git_commit, start_time, end_time
    )

    test_output += s.getvalue()
    if os.path.isfile(checks_log):
        with open(checks_log, 'r') as f:
            checks = f.read()
            if checks:
                test_output += 'Checks:\n' + checks

    os.chdir(top_level)

    if args.log_repo:
        with open(os.path.join(args.log_repo, start_time + '.log'), 'w') as f:
            f.write(test_output)

    if args.stdout:
        print(test_output)

    if args.email:
        notifications.send_plain_text_email(
            test_output,
            subject=checked_out_project + ' integration test',
            **integration_testing.get_cfg()['notification']
        )

    if args.cleanup:
        shutil.rmtree(run_dir)

    return exit_status


if __name__ == '__main__':
    main()
