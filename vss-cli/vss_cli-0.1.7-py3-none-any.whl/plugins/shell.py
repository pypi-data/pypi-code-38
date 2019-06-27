"""Shell plugin for VSS CLI (vss-cli)."""
import click
import os
import logging
from click_repl import repl
from prompt_toolkit.history import FileHistory
from vss_cli.cli import pass_context
from vss_cli import const
from vss_cli.config import Configuration


_LOGGING = logging.getLogger(__name__)


@click.group(
    'shell',
    short_help='REPL interactive shell.',
    invoke_without_command=True
)
@click.option(
    '-i', '--history', type=click.STRING,
    help='File path to save history',
    default=const.DEFAULT_HISTORY,
    envvar='VSS_SHELL_HISTORY',
    required=False
)
@pass_context
def cli(ctx: Configuration, history):
    """REPL interactive shell."""
    ctx.load_config()
    _message_pfix = 'vss'
    _message_sfix = '> '
    # obtain hostname
    _message = f'{_message_pfix} ({ctx.endpoint_name}) {_message_sfix}'
    welcome = r"""
    __   _____ ___
    \ \ / / __/ __|      API Endpoint: {endpoint}
     \ V /\__ \__ \      Tab-completion & suggestions
      \_/ |___/___/      Prefix external commands with "!"
       CLI v{version}        History is saved: {history}

    Exit shell with :exit, :q, :quit, ctrl+d
    """.format(
        version=const.__version__,
        history=history,
        endpoint=ctx.endpoint
    )
    ctx.secho(welcome, fg='blue')
    # create dir for history
    f_path = os.path.expanduser(history or ctx.history)
    dir_name = os.path.dirname(f_path)

    if not os.path.exists(dir_name):
        _LOGGING.warning(
            f'Creating {dir_name} for shell history file'
        )
        os.mkdir(dir_name)
        _LOGGING.warning(
            f'Created {dir_name} for shell history file'
        )
    # run repl
    prompt_kwargs = {
        'history': FileHistory(f_path),
        'message': _message
    }
    repl(
        click.get_current_context(),
        prompt_kwargs=prompt_kwargs,
        allow_internal_commands=True,
        allow_system_commands=True
    )
