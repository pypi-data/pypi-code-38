from __future__ import print_function
from __future__ import division

import os
import sys

import yaml
import civis
import click

from .utils import get_most_recent_run
from .defaults import LASTSCRIPTID_LOC


def _print_script_runs(scriptid):
    """Print the runs for a script.

    Parameters
    ----------
    scriptid : int
        The container script to print the runs for.
    """
    client = civis.APIClient(resources='all')

    try:
        # First get all of the runs.
        runs = client.scripts.list_containers_runs(scriptid)

        fmt = "%- 25s %- 25s %- 25s %- 25s %s"
        head = fmt % ("run id", "started", "finished", "status", "error msg")
        print(head)
        for run in runs:
            print(fmt % (run['id'],
                         run['started_at'] if run['started_at'] else '-',
                         run['finished_at'] if run['finished_at'] else '-',
                         run['state'],
                         run['error'] if run['error'] else '-'))
    except civis.base.CivisAPIError as e:
        print(
            "Could not get script %s runs: %s.%s: %s" % (
                scriptid, e.__module__, e.__class__.__name__, e),
            file=sys.stderr)
        sys.exit(-1)


def _print_script_logs(scriptid, runid=None):
    """Print the logs and information for a script.

    Parameters
    ----------
    scriptid : int
        The script ID to print out.
    runid : int or None, optional
        An optional run ID. If None, then the most recent
        run will be used.
    """
    client = civis.APIClient(resources='all')

    try:
        # get the run details
        runid = runid or get_most_recent_run(scriptid, client=client)

        # Get rest of script details.
        deets = client.scripts.get_containers(scriptid)

        # Make them into pure dicts for dumping to yaml.
        deets = {k: dict(v)
                 if (isinstance(v, civis.response.Response) or
                     isinstance(v, dict)) else v
                 for k, v in deets.items()}

        # Put the name and id at the top so they are easy to see
        print('name:', deets['name'])
        print('id:', deets['id'])
        del deets['name']
        del deets['id']

        # Make the docker command more grep-able.
        print('docker_command:')
        for line in deets['docker_command'].split('\n'):
            line = line.rstrip()
            print('  ' + line)
        del deets['docker_command']

        # now dump the rest.
        print(yaml.dump(deets, default_flow_style=False).strip())

        if runid is not None:
            # Get and print the logs for this run
            resp = client.scripts.list_containers_runs_logs(scriptid, runid)
            print("log file:")
            for r in resp[::-1]:
                print("  [%s] %s" % (r['created_at'], r['message']))
        else:
            print('log file: -')
    except civis.base.CivisAPIError as e:
        print(
            "Could not print script %s logs: %s.%s: %s" % (
                scriptid, e.__module__, e.__class__.__name__, e),
            file=sys.stderr)
        sys.exit(-1)


def _print_scripts(user_ids, state, hidden):
    """List scripts given a list of users.

    This function only lists scripts that are containers.

    Parameters
    ----------
    user_ids : list of ints
        List of user IDs to get jobs for.
        An empty list corresponds to all scripts
        visible to the user making the API call.
    state : str
        List scripts only in this state. Use None to
        get scripts in all states.
    hidden : bool
        If True, display hidden scripts in addition to non-hidden ones.
    """
    client = civis.APIClient(resources='all')

    # Get scripts.
    scripts = []

    def _append_scripts(_hidden):
        _scripts = client.scripts.list(
            limit=50,
            hidden=_hidden,
            status=state,
            order='updated_at',
            type='containers',
            author=','.join(str(u) for u in user_ids) if user_ids else None)
        for s in _scripts:
            scripts.append(s)

    _append_scripts(_hidden=False)
    if hidden:
        _append_scripts(_hidden=True)

    # Print them out.
    fmt_str = "%- 20s %- 20s %- 20s %- 25s %- 25s %- 25s %s"
    head = fmt_str % (
        "id",
        "author",
        "status",
        "created",
        "started",
        "finished",
        "name")
    print(head)

    for s in scripts:
        if user_ids and s['author']['id'] not in user_ids:
            continue

        if s['last_run'] is not None:
            s_tme = s['last_run']['startedAt'] or '-'
            f_tme = s['last_run']['finishedAt'] or '-'
        else:
            s_tme = '-'
            f_tme = '-'
        c_tme = s['created_at'] or '-'

        print(fmt_str % (s['id'],
                         s['author']['username'],
                         s['state'],
                         c_tme,
                         s_tme,
                         f_tme,
                         s['name']))


def _parse_user_ids(users, client):
    """parse a string of users separated by commas into IDS"""
    ids = []
    split_users = users.split(',')
    for u in split_users:
        u = u.strip()
        if len(u) > 0:
            uid = client.users.list(query=u)
            if uid:
                ids.append(uid[0]['id'])
    return ids


def _status(scriptid, mine, user, runs, runid, last, hidden, state):
    """Inspect a civis-compute script.

    If `scriptid` is given, print information about the script IDs
    according to the various other arguments. Otherwise, the status
    of the civis-compute queue is printed.

    Parameters
    ----------
    scriptid : int or None
        The container script ID to inspect.
    mine : bool
        If listing the status of the civis-compute queue, only list containers
        where the current user is the author.
    user : str or None
        A comma-separated list of user names. If given and the status of the
        civis-compute queue is being printed, only list containers by the given
        users.
    runs : bool
        If `scriptid` is given, print the runs for the script.
    runid : int or None
        If give and `runs` is False, print the script logs for a given run.
    last : bool
        If True, print the script logs for the last script submitted at the
        command line.
    hidden : bool
        If True and the status of the civis-compute queue is being printed,
        include hidden scripts in the outputs.
    state : str
        If the status of the civis-compute queue is being printed, then list
        only scripts with this state.
    """

    if runs and runid is not None:
        raise click.UsageError(
            "Only one of `--runs` or `--run-id` can be given!")

    if scriptid is not None and last:
        raise click.UsageError(
            "Only one of `--last` or `scriptid` can be given!")

    if last:
        try:
            with open(os.path.expandvars(os.path.expanduser(
                    LASTSCRIPTID_LOC)), 'r') as fp:
                scriptid = int(fp.read().strip())
        except Exception:
            print('The most recently run script ID could not be found!',
                  file=sys.stderr)
            sys.exit(-1)

    if scriptid is None:
        client = civis.APIClient(resources='all')

        user_ids = []
        if mine:
            user_ids += [client.users.list_me()['id']]

        if user:
            user_ids += _parse_user_ids(user, client)

        _print_scripts(
            user_ids,
            state if state != 'all' else None,
            hidden)
    else:
        if runs:
            _print_script_runs(scriptid)
        else:
            _print_script_logs(scriptid, runid=runid)
