import click
import click_completion
from missinglink.core.config import default_missing_link_folder
from .global_cli import cli

__prev_resolve_ctx = click_completion.resolve_ctx


def __ml_resolve_ctx(_cli, prog_name, args):
    from missinglink.core.context import init_context2
    from missinglink.commands import cli

    def find_top_parent_ctx(current_ctx):
        parent = current_ctx
        while True:
            if current_ctx.parent is None:
                break

            parent = current_ctx.parent
            current_ctx = parent

        return parent

    ctx = __prev_resolve_ctx(cli, prog_name, args)

    top_ctx = find_top_parent_ctx(ctx)

    init_context2(
        ctx,
        top_ctx.params.get('session'),
        top_ctx.params.get('output_format'),
        top_ctx.params.get('config_prefix'),
        top_ctx.params.get('config_file'))

    return ctx


click_completion.resolve_ctx = __ml_resolve_ctx
click_completion.init()


@cli.command('install')
@click.argument('shell', required=False, type=click_completion.DocumentedChoice(click_completion.shells))
def install(shell):
    """Installs TAB completion for the specified shell."""
    from missinglink.legit.path_utils import makedir

    """Install the click-completion-command completion"""
    from missinglink.commands.install import rc_updater

    shell = shell or click_completion.get_auto_shell()

    code = click_completion.get_code(shell)

    file_name = '{dir}/completion.{shell}.inc'.format(dir=default_missing_link_folder(), shell=shell)

    makedir(file_name)

    with open(file_name, 'w') as f:
        f.write(code)

    rc_updater(shell, file_name)
