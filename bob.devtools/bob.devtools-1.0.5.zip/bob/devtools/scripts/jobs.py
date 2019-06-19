#!/usr/bin/env python

import os

import click

from . import bdt
from ..release import get_gitlab_instance

from ..log import verbosity_option, get_logger, echo_normal, echo_info
logger = get_logger(__name__)


@click.command(epilog='''
Examples:

  1. List running jobs on any of our runners

     $ bdt gitlab jobs -vv


  2. List running jobs on a runner defined by its description:

     $ bdt gitlab jobs -vv macmini

''')
@click.argument('name', nargs=-1)
@click.option('-s', '--status', type=click.Choice(['running', 'success',
  'failed', 'canceled']),
    default='running', show_default=True,
    help='The status of jobs we are searching for - one of "running", ' \
        '"success", "failed" or "canceled"')
@verbosity_option()
@bdt.raise_on_error
def jobs(name, status):
    """Lists jobs on a given runner identified by description
    """

    gl = get_gitlab_instance()
    gl.auth()
    user_id = gl.user.attributes['id']

    names = name or [
        'linux-desktop-shell',
        'linux-desktop-docker',
        'linux-server-shell',
        'linux-server-docker',
        'macpro',
        'macmini',
        ]

    # search for the runner(s) to affect
    runners = [k for k in gl.runners.list(all=True) if \
        k.attributes['description'] in names]

    if not runners:
      raise RuntimeError('Cannot find runner with description = %s' % \
          '|'.join(names))

    for runner in runners:
      jobs = runner.jobs.list(all=True, status=status)
      echo_normal('Runner %s (id=%d) -- %d running' % \
          (runner.attributes['description'], runner.attributes['id'],
          len(jobs)))
      for k in jobs:
        echo_info('** job %d: %s (%s), since %s, by %s [%s]' % \
            (k.id, k.attributes['project']['path_with_namespace'],
          k.attributes['name'], k.attributes['started_at'],
          k.attributes['user']['username'], k.attributes['web_url']))
