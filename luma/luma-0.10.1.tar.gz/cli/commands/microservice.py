"""
    These are the sub-commands for a top level object added to the CLI group in 'cli.py'.
    The commands and options are implemented here and the logic behind them resides in the corresponding behavior file.
"""

from cli import pyke, behavior
import click

@click.group(help='A microservice is comprised of microservice-versions. You can share microservices with other orgs giving them access to use the associated versions.')
def microservice():
    pass

@click.command('ls')
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@click.option('--format', '-f', default='{id} {name} {urlRef} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--filter', default='')
@click.option('--page', default=1)
@click.option('--pagesize', default=100)
@click.option('--json/--table', default=False, help='Return raw json from the platform.')
@pyke.auth.profile_context_required
def list(format, profile, json, **kwargs):
    behavior.MicroserviceBehavior(profile=profile, format=format, json=json, **kwargs).list()

@click.command('rm')
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@click.option('--container', '-c', 'microservice', prompt=True, help='The id or the urlRef of the microservice')
@click.option('--format', '-f', default='{id} {name} {urlRef} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json/--table', default=False, help='Return raw json from the platform.')
@pyke.auth.profile_context_required
def delete(microservice, profile, format, json):
    behavior.MicroserviceBehavior(profile=profile, format=format, json=json).delete(microservice)

@click.command('add')
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@click.option('--name', prompt=True, help='The name of the microservice.')
@click.option('--url-ref', prompt=True, help="A unique value for how the microservice will be addressed in a URL.")
@click.option('--icon-file', '-path', type=click.Path(), help='The path to a SVG icon for the microservice.')
@click.option('--format', '-f', default='{id} {name} {urlRef} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json/--table', default=False, help='Return raw json from the platform.')
@pyke.auth.profile_context_required
def create(profile, name, url_ref, icon_file, format, json):
    behavior.MicroserviceBehavior(profile=profile, format=format, json=json).create(name, url_ref, icon_file)

@click.command()
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@click.option('--container', '-c', 'microservice', prompt=True, help='The id or the urlRef of the microservice')
@click.option('--name', default='', help="The new name for the microservice.")
@click.option('--icon-file', '-path', default='', type=click.Path(), help='The path to a new SVG icon for the microservice.')
@click.option('--format', '-f', default='{id} {name} {urlRef} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json/--table', default=False, help='Return raw json from the platform.')
@pyke.auth.profile_context_required
def update(profile, microservice, name, icon_file, format, json):
    behavior.MicroserviceBehavior(profile=profile, format=format, json=json).update(microservice, name, icon_file)

@click.command('access', help="The access command shares and unshares objects with child orgs.")
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@click.option('--container', '-c', 'microservice', prompt=True, help='The id or the urlRef of the microservice being shared/unshared')
@click.option('--add', multiple=True, help="Share with an org. (ID || Org Name)")
@click.option('--rm', multiple=True, help="Un-Share with an org. (ID || Org Name)")
@click.option('--absolute', multiple=True, help='Flush and fill shared with list. (ID || Org Name)')
@click.option('--format', '-f', default='{failed} {sharedWith} {unsharedFrom} {resultingGrantees}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json/--table', default=False, help='Return raw json from the platform.')
@click.option('--current', is_flag=True, help="Returns a list of orgs currently shared with this object.")
@pyke.auth.profile_context_required
def share(microservice, add, rm, absolute, profile, format, json, current):
    behavior.MicroserviceBehavior(profile=profile, format=format, json=json).share(microservice, add, rm, absolute, current)

microservice.add_command(list)
microservice.add_command(create)
microservice.add_command(delete)
microservice.add_command(update)
microservice.add_command(share)
