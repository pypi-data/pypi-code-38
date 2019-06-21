"""
Inspects and manipulates settings files.
"""
from __future__ import print_function

from pprint import pprint
import types

from fabric.api import (
    env,
)

from burlap.decorators import task_or_dryrun


@task_or_dryrun
def show(keyword=''):
    """
    Displays a list of all environment key/value pairs for the current role.
    """
    keyword = keyword.strip().lower()
    max_len = max(len(k) for k in env.iterkeys())
    keyword_found = False
    for k in sorted(env.keys()):
        if keyword and keyword not in k.lower():
            continue
        keyword_found = True
        #print '%s: %s' % (k, env[k])
        print('%s: ' % (k.ljust(max_len),))
        pprint(env[k], indent=4)
    if keyword:
        if not keyword_found:
            print('Keyword "%s" not found.' % keyword)


@task_or_dryrun
def record_manifest():
    """
    Called after a deployment to record any data necessary to detect changes
    for a future deployment.
    """
    data = {}
    # Record settings.
    data['settings'] = dict(
        (k, v)
        for k, v in env.items()
        if not isinstance(v, types.GeneratorType) and k.strip() and not k.startswith('_') and not callable(v)
    )
    # Record tarball hash.
    # Record database migrations.
    # Record media hash.
    return data


def compare_manifest(data=None):
    """
    Called before a deployment, given the data returned by record_manifest(),
    for determining what, if any, tasks need to be run to make the target
    server reflect the current settings within the current context.
    """
