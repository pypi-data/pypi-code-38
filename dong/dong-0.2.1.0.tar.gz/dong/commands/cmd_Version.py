import click
import os
import dong
from dong.utils import get_version

@click.command(help='Print version and exit.', add_help_option=False)
def command():
    path = os.path.dirname(dong.__file__)[0:-4] + 'setup.py'
    version = get_version(path)
    click.echo(f"dong {str(version)}")
