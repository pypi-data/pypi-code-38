#!/usr/bin/env python

import os

import click

from . import bdt
from ..release import get_gitlab_instance

from ..log import verbosity_option, get_logger
logger = get_logger(__name__)


@click.command(epilog='''
Examples:

  1. Disables the runner with description "macmini" for all active projects in group "bob":

     $ bdt gitlab runners -vv bob disable macmini


  2. Enables the runner with description "linux-srv01" on all projects inside group "beat":

     $ bdt gitlab runners -vv beat enable linux-srv01


  3. Enables the runner with description "linux-srv02" on a specific project:

     $ bdt gitlab runners -vv bob/bob.extension enable linux-srv02

''')
@click.argument('target')
@click.argument('cmd', type=click.Choice(['enable', 'disable']))
@click.argument('name')
@click.option('-d', '--dry-run/--no-dry-run', default=False,
    help='Only goes through the actions, but does not execute them ' \
        '(combine with the verbosity flags - e.g. ``-vvv``) to enable ' \
        'printing to help you understand what will be done')
@verbosity_option()
@bdt.raise_on_error
def runners(target, cmd, name, dry_run):
    """Enables and disables runners on whole gitlab groups or single projects
    """

    gl = get_gitlab_instance()
    gl.auth()
    user_id = gl.user.attributes['id']

    if '/' in target:  #it is a specific project
      packages = [gl.projects.get(target)]
      logger.debug('Found gitlab project %s (id=%d)',
          packages[0].attributes['path_with_namespace'], packages[0].id)

    else:  #it is a group - get all projects
      logger.warn('Retrieving group by name - may take long...')
      group = gl.groups.get(target)
      logger.debug('Found gitlab group %s (id=%d)', group.attributes['path'],
          group.id)
      logger.warn('Retrieving all projects (with details) from group ' \
          '%s (id=%d)...', group.attributes['path'], group.id)
      packages = [gl.projects.get(k.id) for k in \
          group.projects.list(all=True, simple=True)]
      logger.info('Found %d projects under group %s', len(packages),
          group.attributes['path'])

    # search for the runner to affect
    the_runner = [k for k in gl.runners.list(all=True) if \
        k.attributes['description'] == name]
    if not the_runner:
      raise RuntimeError('Cannot find runner with description = %s', name)
    the_runner = the_runner[0]
    logger.info('Found runner %s (id=%d)',
        the_runner.attributes['description'], the_runner.attributes['id'])

    for k in packages:
      logger.info('Processing project %s (id=%d)',
          k.attributes['path_with_namespace'], k.id)

      if cmd == 'enable':

        #checks if runner is not enabled first
        enabled = False
        for l in k.runners.list(all=True):
          if l.id == the_runner.id:  #it is there already
            logger.warn('Runner %s (id=%d) is already enabled for project %s',
                l.attributes['description'], l.id,
                k.attributes['path_with_namespace'])
            enabled = True
            break

        if not enabled:  #enable it
          if not dry_run:
            k.runners.create({'runner_id': the_runner.id})
          logger.info('Enabled runner %s (id=%d) for project %s',
              the_runner.attributes['description'], the_runner.id,
              k.attributes['path_with_namespace'])


      elif cmd == 'disable':

        #checks if runner is not already disabled first
        disabled = True
        for l in k.runners.list(all=True):
          if l.id == the_runner.id:  #it is there already
            logger.debug('Runner %s (id=%d) is enabled for project %s',
                l.attributes['description'], l.id,
                k.attributes['path_with_namespace'])
            disabled = False
            break

        if not disabled:  #enable it
          if not dry_run:
            k.runners.delete(the_runner.id)
          logger.info('Disabled runner %s (id=%d) for project %s',
              the_runner.attributes['description'], the_runner.id,
              k.attributes['path_with_namespace'])
