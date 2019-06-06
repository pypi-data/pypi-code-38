import click
import os
import semver

import angreal
from angreal import Git

here = os.path.dirname(__file__)


@angreal.command()
@angreal.option('--major', is_flag=True, help='Make a major bump (0.0.0 -> 1.0.0)')
@angreal.option('--minor', is_flag=True, help='Make a major bump (0.0.0 -> 0.1.0)')
@angreal.option('--patch', is_flag=True, help='Make a major bump (0.0.0 -> 0.0.1)')
def angreal_cmd(major, minor, patch):
    """
    bump the current package version
    """

    os.chdir(os.path.join(here, '..'))
    VERSION_FILE = os.path.join('{{angreal._cleaned_name}}', 'VERSION')

    # what's our version
    VERSION = open(VERSION_FILE).read().strip()

    # bump as requested
    if not (major or minor or patch):
        angreal.echo(click.style('No bump settings provided !', fg='red'))
        exit(1)

    if major:
        VERSION = semver.bump_major(VERSION)
    if minor:
        VERSION = semver.bump_minor(VERSION)
    if patch:
        VERSION = semver.bump_patch(VERSION)

    # save to disk
    with open(VERSION_FILE, 'w') as f:
        print(VERSION, file=f)

    git = Git()
    git.commit('-am', 'version bump applied via angreal')
    angreal.echo(click.style('VERSION bumped to {}'.format(VERSION), fg='green'))
    return
