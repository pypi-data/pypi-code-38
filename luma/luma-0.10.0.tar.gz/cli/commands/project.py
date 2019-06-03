"""
    These are the sub-commands for a top level object added to the CLI group in 'cli.py'.
    The commands and options are implemented here and the logic behind them resides in the corresponding behavior file.
"""

from cli import pyke, behavior
import click

@click.group(help='Commands related to developing, managing and publishing experiences.')
def project():
  pass

@click.command('init', help="Initializes the current directory as a lumavate project")
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@pyke.auth.profile_context_required
def init(**kwargs):
  behavior.ProjectBehavior(**kwargs).init()

@click.command('get-qr', help="Display the QR activation code in the terminal")
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@pyke.auth.profile_context_required
def get_qr(**kwargs):
  behavior.ProjectBehavior(**kwargs).display_qr()



project.add_command(init)
project.add_command(get_qr)
