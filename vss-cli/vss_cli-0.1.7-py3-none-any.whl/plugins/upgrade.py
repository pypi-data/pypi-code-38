"""Upgrade plugin for VSS CLI (vss-cli)."""
import logging
from subprocess import call

import click
from vss_cli import vssconst
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.utils.emoji import EMOJI_UNICODE

_LOGGING = logging.getLogger(__name__)


@click.group(
    'upgrade',
    invoke_without_command=True,
    short_help='Upgrade VSS CLI and dependencies.')
@click.argument(
    'upstream',
    type=click.Choice(
        ['stable', 'develop', 'branch']
    ),
    default='stable'
)
@click.option(
    '--git-branch', '-b',
    help='GitLab repository branch',
    required=False
)
@pass_context
def cli(ctx: Configuration, upstream, git_branch):
    """Upgrade existing install of VSS CLI to the latest version
    (experimental). For example, to upgrade to the stable version:

    vss-cli upgrade stable

    To upgrade VSS CLI to the latest develop build:

    vss-cli upgrade develop

    To upgrade to a given official vss-cli GitLab repository:

    vss-cli upgrade --git-branch=issue-145 branch


    """
    lookup = {
        'stable': {
            'pkg': 'vss-cli',
            'args': ['--upgrade']
        },
        'develop': {
            'pkg': 'vss-cli',
            'args': [
                '--upgrade',
                '--index-url',
                'https://test.pypi.org/legacy/'
            ]
        },
        'branch': {
            'pkg': f'git+https://gitlab-ee.eis.utoronto.ca'
            f'/vss/vss-cli.git@{git_branch}',
            'args': ['--upgrade']
        }
    }
    try:
        cmd_lookup = lookup[upstream]
        if upstream == 'branch':
            if not git_branch:
                raise click.BadOptionUsage(
                    'branch',
                    'Missing --branch/-b option. '
                    'Try master or develop.'
                )
    except ValueError as ex:
        _LOGGING.error(f'Invalid upstream {upstream}: {ex}')
        raise click.BadArgumentUsage(
            f'Invalid upstream {upstream}'
        )
    # assemble command
    cmd_args_str = ' '.join(cmd_lookup['args'])
    cmd_bin = ctx.get_pip_binary()
    # execute command
    cmd_str = f"{cmd_bin} install {cmd_args_str} {cmd_lookup['pkg']}"
    _LOGGING.debug(f'Executing {cmd_str}')
    # calling command
    exit_code = call(
        cmd_str,
        shell=True)
    if exit_code > 0:
        raise click.ClickException(
            f'Could not perform upgrade, please try: '
            f'\n\t{cmd_str}')
    else:
        _LOGGING.debug(
            f'Successfully executed upgrade command: {cmd_str}'
        )
    # all done
    ctx.secho(
        f'Successfully executed upgrade command '
        f'{EMOJI_UNICODE.get(":white_heavy_check_mark:")}',
        fg='green'
    )
