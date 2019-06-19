#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Main entry point for bdt
"""

import os
import pkg_resources

import click
from click_plugins import with_plugins

from ..log import setup
logger = setup('bob')


class AliasedGroup(click.Group):
  ''' Class that handles prefix aliasing for commands '''
  def get_command(self, ctx, cmd_name):
    rv = click.Group.get_command(self, ctx, cmd_name)
    if rv is not None:
      return rv
    matches = [x for x in self.list_commands(ctx)
               if x.startswith(cmd_name)]
    if not matches:
      return None
    elif len(matches) == 1:
      return click.Group.get_command(self, ctx, matches[0])
    ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))


def raise_on_error(view_func):
    """Raise a click exception if returned value is not zero.

    Click exits successfully if anything is returned, in order to exit properly
    when something went wrong an exception must be raised.
    """

    from functools import wraps

    def _decorator(*args, **kwargs):
        value = view_func(*args, **kwargs)
        if value not in [None, 0]:
            exception = click.ClickException("Error occured")
            exception.exit_code = value
            raise exception
        return value
    return wraps(view_func)(_decorator)


# warning: must set LANG and LC_ALL before using click
# see: https://click.palletsprojects.com/en/7.x/python3/
if 'LANG' not in os.environ:
  os.environ['LANG'] = 'en_US.UTF-8'
if 'LC_ALL' not in os.environ:
  os.environ['LC_ALL'] = 'en_US.UTF-8'

@with_plugins(pkg_resources.iter_entry_points('bdt.cli'))
@click.group(cls=AliasedGroup,
             context_settings=dict(help_option_names=['-?', '-h', '--help']))
def main():
    """Bob Development Tools - see available commands below"""

    from ..constants import CACERT
    from ..bootstrap import set_environment

    # certificate setup: required for gitlab API interaction
    set_environment('SSL_CERT_FILE', CACERT, os.environ)
    set_environment('REQUESTS_CA_BUNDLE', CACERT, os.environ)
