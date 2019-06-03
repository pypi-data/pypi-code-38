"""
    These are the sub-commands for a top level object added to the CLI group in 'cli.py'.
    The commands and options are implemented here and the logic behind them resides in the corresponding behavior file.
"""

from cli import pyke, behavior
import click

@click.group('component-set', help='A component-set is comprised of component-set-versions. You can share component-sets with other orgs giving them access to use the associated versions.')
def component_set():
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
    behavior.ComponentSetBehavior(profile=profile, format=format, json=json, **kwargs).list()

@click.command('rm')
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@click.option('--component-set', '-cs', prompt=True, help='The ID or the urlRef of the component-set to delete')
@click.option('--format', '-f', default='{id} {name} {urlRef} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json/--table', default=False, help='Return raw json from the platform.')
@pyke.auth.profile_context_required
def delete(component_set, profile, format, json):
    behavior.ComponentSetBehavior(profile=profile, format=format, json=json).delete(component_set)

@click.command('add')
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@click.option('--name', prompt=True, help='The name of the component set')
@click.option('--url-ref', prompt=True, help="A unique value for how the component-set will be addressed in a URL.")
@click.option('--icon-file', '-path', type=click.Path(), help='The path to an SVG icon for the component set')
@click.option('--format', '-f', default='{id} {name} {urlRef} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json/--table', default=False, help='Return raw json from the platform.')
@pyke.auth.profile_context_required
def create(profile, name, url_ref, icon_file, format, json):
    behavior.ComponentSetBehavior(profile=profile, format=format, json=json).create(name, url_ref, icon_file)

@click.command()
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@click.option('--component-set', '-cs', prompt=True, help='The ID or the urlRef of the component-set to update')
@click.option('--name', default='', help='The name of the component set')
@click.option('--icon-file', '-path', default='', type=click.Path(), help='The path to an SVG icon for the component set')
@click.option('--format', '-f', default='{id} {name} {urlRef} {createdAt}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json/--table', default=False, help='Return raw json from the platform.')
@pyke.auth.profile_context_required
def update(component_set, name, icon_file, profile, format, json):
    behavior.ComponentSetBehavior(profile=profile, format=format, json=json).update(component_set, name, icon_file)

@click.command('access', help="The access command shares and unshares objects with child orgs.")
@click.option('--profile', '-p', prompt=True, help='The name of the profile to use as the context for the command.', autocompletion=pyke.auth.get_profile_names)
@click.option('--component-set', '-cs', prompt=True, help='The id or the urlRef of the component-set being shared/unshared')
@click.option('--add', multiple=True, help="Share with an org. (ID || Org Name)")
@click.option('--rm', multiple=True, help="Un-Share with an org. (ID || Org Name)")
@click.option('--absolute', multiple=True, help='Flush and fill shared with list. (ID || Org Name)')
@click.option('--format', '-f', default='{failed} {sharedWith} {unsharedFrom} {resultingGrantees}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json/--table', default=False, help='Return raw json from the platform.')
@click.option('--current', is_flag=True, help="Returns a list of orgs currently shared with this object.")
@pyke.auth.profile_context_required
def share(component_set, add, rm, absolute, profile, format, json, current):
    behavior.ComponentSetBehavior(profile=profile, format=format, json=json).share(component_set, add, rm, absolute, current)

component_set.add_command(list)
component_set.add_command(create)
component_set.add_command(delete)
component_set.add_command(update)
component_set.add_command(share)
