"""
    These are the sub-commands for a top level object added to the CLI group in 'cli.py'.
    The commands and options are implemented here and the logic behind them resides in the corresponding behavior file.
"""

from cli import pyke, behavior
import click

@click.group(help='Experience Collection related commands.')
def experience_collection():
  pass

@click.command('ls', help="List the experience collections related to the selected profile.")
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@click.option('--format', '-f', default='{id} {name} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--filter', default='')
@click.option('--page', default=1)
@click.option('--pagesize', default=100)
@click.option('--json/--table', default=False, help='Return raw json from the platform.')
@pyke.auth.profile_context_required
def list(**kwargs):
  behavior.ExperienceCollectionBehavior(**kwargs).list()

experience_collection.add_command(list)
