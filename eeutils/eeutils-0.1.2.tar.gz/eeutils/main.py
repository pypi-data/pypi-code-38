import click
import click_completion


AVAILABLE_PROGRAMS = [
    'eeutils', 'eebash', 'eeodoo', 'eegit',
]


def custom_startswith(string, incomplete):
    """
    A custom completion matching that supports:
        * Matching anywhere on the string
        * Case insensitive matching
    """
    string = string.lower()
    incomplete = incomplete.lower()
    return incomplete in string


click_completion.core.startswith = custom_startswith
click_completion.init()


@click.group()
def eeutils():
    """Completion Installation"""
    pass


@eeutils.command()
@click.option(
    '--append/--overwrite',
    help="Append the completion code to the file", default=None)
@click.option(
    '-i', '--case-insensitive/--no-case-insensitive',
    help="Case insensitive completion")
@click.argument(
    'shell', required=False,
    type=click_completion.DocumentedChoice(click_completion.core.shells))
@click.argument(
    'path', required=False)
def install(append, case_insensitive, shell, path):
    """Install the click-completion-command completion"""
    extra_env = {
        '_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE': 'ON',
    } if case_insensitive else {}
    for program in AVAILABLE_PROGRAMS:
        shell, path = click_completion.core.install(
            shell=shell, path=path, append=append, extra_env=extra_env,
            prog_name=program)

    click.echo('%s completion installed in %s' % (shell, path))


@click.group()
def bash():
    """Bash Utilities."""
    pass


@click.group()
def odoo():
    """Odoo Utilities."""
    pass


@click.group()
def git():
    """Git Utilities."""
    pass
